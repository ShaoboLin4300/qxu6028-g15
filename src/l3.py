"""L3 - two-dimensional inverse problem: zero-mean uniformity map.

Method (Methods Guide, pages 10-12)
----------------------------------
* d = A m with A (128 x 100); every row of A sums to numerical zero, so a
  uniform offset is invisible and the map must be constrained to zero mean
* solve the smoothness-regularised problem
      min ||A m - d||^2 + eta ||L m||^2   with  mean(m) = 0
  by projecting out the constant mode with P = I - u u^T (u = 1/sqrt(N))
* reference eta from the Guide: eta0 = 1e-2 ||A||_2^2 / ||L||_2^2
* resolution: inject a zero-mean single-pixel feature, forward-project with A,
  reconstruct with the same eta and solver, report the positive-lobe FWHM
* detection limit: 500 noise-only vectors drawn from the channel-wise repeat
  standard deviation, reconstructed identically; delta95 = 95th percentile of
  max|m_noise|
* decision: a = max|m| against the announced threshold tau, with an explicit
  confidence statement from delta95
"""

from __future__ import annotations

import numpy as np

from . import common as C


def projector(N):
    u = np.ones((N, 1)) / np.sqrt(N)
    return np.eye(N) - u @ u.T


def eta_reference(A, L):
    return 1e-2 * np.linalg.norm(A, 2) ** 2 / np.linalg.norm(L, 2) ** 2


def reconstruct(A, L, P, eta, dvec, N):
    M = P @ (A.T @ A + eta * (L.T @ L)) @ P + 1e-9 * np.eye(N)
    b = P @ (A.T @ dvec)
    m = np.linalg.lstsq(M, b, rcond=None)[0]
    return m - m.mean()


def pixel_coords(npix=10):
    """Pixel centres in probe-pitch units (region 6s x 6s, s = probe pitch)."""
    c = np.linspace(-2.7, 2.7, npix)
    X, Y = np.meshgrid(c, c)          # X varies along columns (j), Y along rows (i)
    return X.ravel(), Y.ravel()


def fwhm_from_map(mhat, npix, centre_pixel, pitch=0.6):
    """FWHM of the positive lobe, from weighted second moment (Guide, p.12)."""
    Q = np.asarray(mhat).reshape(npix, npix)
    w = np.maximum(Q, 0.0)
    if w.sum() <= 0:
        return float("nan")
    ci, cj = divmod(centre_pixel, npix)
    ii, jj = np.meshgrid(np.arange(npix), np.arange(npix), indexing="ij")
    r2 = ((ii - ci) ** 2 + (jj - cj) ** 2) * pitch ** 2
    sigma2 = (w * r2).sum() / (2.0 * w.sum())
    return float(2.355 * np.sqrt(sigma2))


def _merge_features(m, npix, threshold, X, Y):
    """Connected components of same-sign pixels above |threshold|.

    Neighbouring pixels are merged into one feature (Guide, page 11) instead of
    reporting every pixel as a separate defect.
    """
    Q = m.reshape(npix, npix)
    seen = np.zeros((npix, npix), bool)
    feats = []
    for sign, mask in (("positive", Q > threshold), ("negative", Q < -threshold)):
        for i0 in range(npix):
            for j0 in range(npix):
                if not mask[i0, j0] or seen[i0, j0]:
                    continue
                stack, comp = [(i0, j0)], []
                seen[i0, j0] = True
                while stack:
                    i, j = stack.pop()
                    comp.append((i, j))
                    for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        a, b = i + di, j + dj
                        if 0 <= a < npix and 0 <= b < npix and mask[a, b] and not seen[a, b]:
                            seen[a, b] = True
                            stack.append((a, b))
                idx = [i * npix + j for i, j in comp]
                amp = float(m[idx][np.argmax(np.abs(m[idx]))])
                # amplitude-weighted centroid in probe-pitch coordinates
                w = np.abs(m[idx])
                feats.append({
                    "sign": sign,
                    "amplitude": amp,
                    "x_probe_pitch": float((w * X[idx]).sum() / w.sum()),
                    "y_probe_pitch": float((w * Y[idx]).sum() / w.sum()),
                    "size_pixels": len(idx),
                })
    feats.sort(key=lambda f: -abs(f["amplitude"]))
    return feats


def run(ds, tau=C.TAU, npix=None):
    A, d = ds["A"], ds["d"]
    dbar = d.mean(axis=0)
    N = A.shape[1]
    if npix is None:
        npix = int(ds["l3_meta"].get("npix", 10))
    L = C.gradient_matrix(npix)
    P = projector(N)
    eta0 = eta_reference(A, L)

    m = reconstruct(A, L, P, eta0, dbar, N)
    Q = m.reshape(npix, npix)
    X, Y = pixel_coords(npix)

    # ---- regularisation sensitivity ------------------------------------
    mults = [0.01, 0.1, 1.0, 10.0, 100.0]
    sens = []
    for k in mults:
        mk = reconstruct(A, L, P, k * eta0, dbar, N)
        sens.append({
            "eta": float(k * eta0), "eta_over_eta0": k,
            "residual_norm": float(np.linalg.norm(A @ mk - dbar)),
            "roughness_norm": float(np.linalg.norm(L @ mk)),
            "max_abs_m": float(np.max(np.abs(mk))),
        })

    # ---- noise and detection limit -------------------------------------
    sigma_j = d.std(axis=0, ddof=1)
    sigma_norm = float(np.linalg.norm(sigma_j))
    rng = np.random.default_rng(C.NOISE_SEED)
    maxima = np.empty(C.N_NOISE)
    for n in range(C.N_NOISE):
        nvec = rng.normal(0.0, sigma_j)
        mn = reconstruct(A, L, P, eta0, nvec, N)
        maxima[n] = np.max(np.abs(mn))
    delta95 = float(np.percentile(maxima, 95))

    # ---- features ------------------------------------------------------
    amp = float(np.max(np.abs(m)))
    # noise-linked threshold is far below the amplitude, so features are also
    # reported after removing the global plane, which is a separate, resolvable
    # degree of freedom of the map
    B = np.column_stack([X, Y])
    coef, *_ = np.linalg.lstsq(B, m, rcond=None)
    m_tilt = B @ coef
    m_loc = m - m_tilt

    feats_loc = _merge_features(m_loc, npix, 0.30 * np.max(np.abs(m_loc)), X, Y)
    for f in feats_loc:
        f["space"] = "tilt-removed (localised defect)"
    feats_raw = _merge_features(m, npix, 0.30 * amp, X, Y)
    for f in feats_raw:
        f["space"] = "raw zero-mean map (includes global tilt)"

    i_max, i_min = int(np.argmax(m)), int(np.argmin(m))

    # ---- resolution ----------------------------------------------------
    res, psf_map, psf_pixel = [], None, None
    for pix in (int(np.argmin(np.hypot(X, Y))), 27):
        q = np.zeros(N)
        q[pix] = 1.0
        q -= q.mean()
        mq = reconstruct(A, L, P, eta0, A @ q, N)
        if psf_map is None:
            psf_map, psf_pixel = mq, pix
        res.append({"pixel": pix, "x": float(X[pix]), "y": float(Y[pix]),
                    "fwhm_probe_pitch": fwhm_from_map(mq, npix, pix)})
    resolution = max(r["fwhm_probe_pitch"] for r in res)

    # ---- decision ------------------------------------------------------
    if amp + delta95 < tau:
        decision, conf = True, "CLEAR PASS"
    elif amp - delta95 > tau:
        decision, conf = False, "CLEAR FAIL"
    else:
        decision, conf = None, "BORDERLINE"
    confidence = (
        f"Threshold tau={tau:g} ({tau*100:.1f}% of the reference conductivity, "
        f"announced in Session 3). a=max|m|={amp:.4e}, delta95={delta95:.4e} "
        f"-> {conf} (a+delta95={amp+delta95:.4e}, a-delta95={amp-delta95:.4e})"
    )

    result = {
        "map": [float(v) for v in m],
        "features": feats_raw + feats_loc,
        "resolution_probe_pitch": resolution,
        "detection_limit_fraction": delta95,
        "pass": decision if decision is not None else False,
        "confidence": confidence,
    }

    diagnostics = {
        "npix": npix,
        "eta0": float(eta0),
        "eta_used": float(eta0),
        "rank_A": int(np.linalg.matrix_rank(A)),
        "max_abs_row_sum_A": float(np.max(np.abs(A.sum(axis=1)))),
        "map_mean": float(m.mean()),
        "max_abs_map": amp,
        "argmax_pixel": {"x": float(X[i_max]), "y": float(Y[i_max]), "value": float(m[i_max])},
        "argmin_pixel": {"x": float(X[i_min]), "y": float(Y[i_min]), "value": float(m[i_min])},
        "tilt_coefficients_per_pitch": {"x": float(coef[0]), "y": float(coef[1])},
        "tilt_max_abs": float(np.max(np.abs(m_tilt))),
        "localised_max_abs": float(np.max(np.abs(m_loc))),
        "map_tilt": [float(v) for v in m_tilt],
        "map_localised": [float(v) for v in m_loc],
        "residual_norm_used_eta": float(np.linalg.norm(A @ m - dbar)),
        "noise_norm": sigma_norm,
        "noise_median_sigma": float(np.median(sigma_j)),
        "noise_seed": C.NOISE_SEED,
        "delta95": delta95,
        "eta_sensitivity": sens,
        "resolution_tests": res,
        "psf_map": psf_map.tolist(),
        "psf_pixel": int(psf_pixel),
        "noise_maxima": maxima.tolist(),
        "tau": tau,
        "a_plus_delta95": amp + delta95,
        "a_minus_delta95": amp - delta95,
        "decision": conf,
        "map_2d": Q.tolist(),
    }

    # Zero-mean constraint is a hard requirement
    assert abs(float(m.mean())) < 1e-12, "reconstruction must have zero mean"
    assert len(result["map"]) == N and np.all(np.isfinite(result["map"]))
    return result, diagnostics
