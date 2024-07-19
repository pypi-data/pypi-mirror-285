
function solve(prob; autodiff=true, history=nothing, comprehensive=true, verbose=false, plotpath=nothing, _time=true, kwargs...)
    t0 = ignore() do
        time()
    end
    @unpack dx, dt, u0, field_padding, geometry_padding, subpixel_averaging, source_instances, geometry, monitor_instances, transient_duration, steady_state_duration, d, n = prob

    sz = size(first(values(geometry)))
    points = prod(sz)
    steps = (transient_duration + steady_state_duration) / dt |> round
    println("$points points x $steps steps = $(points*steps) point-steps")
    p = geometry
    _gpu = isa(first(values(p)), AbstractGPUArray)
    p = apply(geometry_padding, p)
    # global aaaaaaaaa = p
    # if _gpu
    #     ignore() do
    #         p = gpu(p)
    #     end
    # end
    p = apply(subpixel_averaging, p)
    global aaaaaaaada = p


    Δ = [transient_duration, steady_state_duration]
    T = cumsum(Δ)
    Enames = keys(u0.E)
    Hnames = keys(u0.H)
    # extrema(abs.(prob.source_instances[1]._g.Jy))

    # if save
    _update = !autodiff ? update! : update
    h = []

    # run simulation
    u = reduce(0:dt:T[1], init=deepcopy(u0)) do u, t
        # save && push!(h, u)
        _update(u, p, t, dx, dt, field_padding, source_instances;)
    end

    u, mode_fields, total_powers = reduce(T[1]+dt:dt:T[2], init=(u, 0, 0)) do (u, mode_fields, tp), t
        # save && push!(h, u)
        mode_fields_ = [
            [
                begin
                    # λ = dispersion_compensation(dx, dt, n, λ)
                    # E = dict([k => u[k, m] for k = Enames])
                    # H = dict([k => u[k, m] for k = Hnames])
                    # (; E, H)
                    E = [u[k, m] |> F for k = Enames]
                    H = [u[k, m] |> F for k = Hnames]
                    # global aaab, bbbb = E, H
                    [E, H] * cispi(-2t / λ)
                end for λ = m.wavelength_modes |> keys]
            for m = monitor_instances
        ]
        tp_ = map(monitor_instances) do m
            E = [u[k, m] for k = Enames]
            H = [u[k, m] for k = Hnames]
            mean(sum((E × H) .* normal(m))) * area(m)
        end

        (
            _update(u, p, t, dx, dt, field_padding, source_instances),
            mode_fields + dt / Δ[2] * mode_fields_,
            tp + dt / Δ[2] * tp_,
        )
    end

    v = map(mode_fields, monitor_instances) do mf, m
        map(mf, values(m.wavelength_modes)) do u, wm
            # E = values(u.E)
            # H = values(u.H)
            E, H = u
            if d == 2
                if polarization == :TE
                    # global E, H
                    Ex, Hy, Ez = invreframe(frame(m), vcat(E, H))
                    Ex += 0sum(Ez[1:2])
                    Hy += 0sum(Ez[1:2])
                    # end
                    _mode = (; Ex, Hy, Ez)
                else
                    Hx, Ey, Hz = invreframe(frame(m), vcat(H, E))
                    Hx += 0real(Hz[1])
                    Ey += 0real(Hz[1])
                    _mode = (; Hx, Ey, Hz)
                end
            elseif d == 3
                Ex, Ey, Ez, = invreframe(frame(m), E)
                Hx, Hy, Hz = invreframe(frame(m), H)
                _mode = (; Ex, Ey, Ez, Hx, Hy, Hz)
            end
            # _mode = keepxy(_mode)
            c = mode_decomp.(wm, (_mode,), dx)
            fp = [abs(v[1])^2 for v = c]
            rp = [abs(v[2])^2 for v = c]
            _mode, c, fp, rp
        end
    end
    modes = [[v[1] for v = v] for v in v]
    mode_coeffs = [[v[2] for v = v] for v in v]
    forward_mode_powers = [[v[3] for v = v] for v in v]
    reverse_mode_powers = [[v[4] for v = v] for v in v]

    fields = u
    if verbose
        @show forward_mode_powers, reverse_mode_powers, total_powers
    end
    if !isnothing(plotpath)

    end
    # if _time
    #     ignore() do
    #         println("simulation took: ", time() - t0)
    #     end
    # end
    return (; fields, geometry, modes, mode_coeffs, forward_mode_powers, reverse_mode_powers, total_powers)
end