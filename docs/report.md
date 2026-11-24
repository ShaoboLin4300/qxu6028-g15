# What a wafer is really like: extraction scale, density-of-states class and spatial uniformity from simulated transport

**QXU6028 Polymer Devices — virtual-laboratory group coursework, AY 2026–27**
Group G15 · Lin Shaobo 2023304300 · Miao Shize 2023304317 · Wang Yuzhe 2023304283 · Xu Wenjie 2023304282
Repository: https://github.com/ShaoboLin4300/qxu6028-g15 · Commit that produced these numbers: see `outputs/regular/results.json → pipeline_commit`.

---

## 1. Context and question

A characterisation team is given sheet-resistance and Hall data from a simulated
graphene-on-sapphire wafer [1] and has to answer three questions that a customer
would actually ask. First, what carrier density and mobility does the wafer
have, given that the datasheet used a textbook band-edge count. Second, is the
material gapless or gapped, and how far did the Fermi level drift while the
series was measured. Third, where is the wafer non-uniform, what can the probe
resolve, and does it meet the 3.0 % uniformity specification announced in
Session 3.

The three questions share one theme: none of the reported numbers is a property
of the material alone. Each is the output of an extraction model — an
integration limit, a density-of-states class, a regularisation strength — and
the model choice moves the number. The report therefore states each model,
quantifies how much the answer depends on it, and separates what the data
support from what they cannot decide.

## 2. L1 — the counting convention sets the scale

**Question.** The datasheet used the band-edge carrier count. By how much is the
sensor sensitivity mis-stated at the operating point?

**Method.** Both counts use the same linear density of states $g(E)=cE$ and the
same finite-temperature Fermi function; only the lower limit of integration
changes. The band-edge count integrates from the Dirac point, the
Fermi-referenced count from the Fermi level itself, that is from $E_F$ to
2.5 eV, with $N_A = 3.816\times10^{15}$ cm$^{-2}$ and
$k_B = 8.617333\times10^{-5}$ eV K$^{-1}$.
Both integrals were evaluated on 20 001 points with the trapezoidal rule and
cross-checked against the closed form
$n_F = N_Ac k_BT\,[E_F\ln 2 + (\pi^2/12)k_BT]$, which agree to $4\times10^{-7}$.
The correction factor $C=n_{\rm band}/n_F$ follows, and because
$\mu = 1/(e n \rho)$ [2] at a fixed sheet resistivity, $\mu_F = C\,\mu_B$: the same
factor multiplies the mobility. The operating point $E_{F,\rm op}=0.101816$ eV
was taken from `L1_params.json`, not from the nearest row of the sweep.

**Result.** The published gates are reproduced: the ratio is 1.0000 at
neutrality, 2.0049 at 0.073 eV, 2.5988 at 0.100 eV and 5.1044 at 0.200 eV. The
ratio passes 2 at 72.8 meV and 4 at 157.3 meV (Figure 1a). At the operating
point $C = 2.6408$, so $n_F = 3.801\times10^{11}$ cm$^{-2}$ against the
band-edge $1.004\times10^{12}$ cm$^{-2}$, and the mobility rises from
$2.403\times10^4$ to $6.346\times10^4$ cm$^2$ V$^{-1}$ s$^{-1}$ at $\rho = 258.8\ \Omega/\square$.

**Why the factor grows.** Raising $E_F$ excludes an ever larger slice of
occupied states between the Dirac point and $E_F$. At neutrality the two limits
coincide and the factor is exactly one; as $E_F$ rises the excluded population
grows, so $C$ rises monotonically. The ratio is
independent of the DoS slope $c$, which multiplies both integrals — a useful
invariance check.

**Uncertainty and checks.** Recomputing the band-edge column from the metadata
reproduces the supplied column to $4\times10^{-12}$ relative. Truncating the
integral at 2.5 eV is harmless at 300 K ($E_{\max}\approx 97\,k_BT$). The
dominant uncertainty is definitional, not numerical: the result is exact *for this
model*, which assumes a single linear DoS slope across the sweep.

**Device advice.** Under a stated response model $S \propto 1/n$ — the sensitivity
of a carrier-density sensor — the datasheet understates the response by
$C=2.64$ at this operating point, i.e. by 164 %. A specification written from
band-edge counts would therefore under-predict the change in signal for a given
change in sheet resistance by the same factor. This holds only while the
linear-DoS, single-band picture holds; a gapped or disordered DoS breaks the
proportionality and the factor must be re-derived.

**Table 1.** L1 checks and the operating point. The check column reproduces the values issued with the data.

| $E_F$ (eV) | $n_{\rm band}/n_F$ | check | role |
|---|---|---|---|
| 0.000 | 1.0000 | 1.00 | neutrality: limits coincide |
| 0.073 | 2.0049 | 2.00 | the $C=2$ crossing |
| 0.100 | 2.5988 | 2.60 | mid-sweep check |
| 0.200 | 5.1044 | 5.10 | high doping |
| 0.1018 | 2.6408 | – | reported operating point |

[[fig:1]]

## 3. L2 — gapless cone or hard gap

**Question.** Is the material gapless or gapped, how large is any gap, and how
did the Fermi level move during the series?

**Method.** The three repeats at each index were averaged for the central
estimate and their standard deviation kept for the bootstrap; Figure 2 shows the
raw repeats in acquisition order, with the pair of indices bracketing the $R_H$
sign change marked. $R_H$ and $R_s$ were normalised *separately*, each by its own
maximum, and the sign of $R_H$ was preserved. Separate normalisation matters: the channels differ tenfold, so a shared scale
would let $R_s$ dominate and hide the Hall sign. A
library of normalised curves [3] was built once — an ideal cone $g=c|E|$ and
symmetric hard-gap models $g=c(|E|-E_g/2)$ outside $|E|\le E_g/2$, with
$E_g/k_BT$ from 0.50 to 8.00 in steps of 0.25, on 400 candidate Fermi levels from
$-8\,k_BT$ to $+9\,k_BT$. Each pair was assigned the nearest point on each curve in the normalised
$(R_H,R_s)$ plane; Figure 3 shows the library and Figure 4 the resulting fit. The selection rule was fixed in advance: a
gap is claimed only when $r_{\rm gap} < 0.85\,r_{\rm cone}$ *and*
$E_g \ge 1\,k_BT$.




**Result.** The cone wins on both counts. The cone residual is
$r_{\rm cone}=0.01563$; the best hard-gap model reaches only
$r_{\rm gap}=0.01970$, a ratio of 1.26, far from the 0.85 improvement required (Table 2). The assigned Fermi
level moves from $-71.3$ to $+145.7$ meV across the series (Figure 6), crossing
zero at index 12, exactly where the measured $R_H$ changes sign. The chosen model
is therefore *cone*, $E_g=0$, and none of the 200 bootstrap replicates selected a
hard gap. The bootstrap confirms it: every replicate reselects the cone (Figure 7).

[[fig:2]]





**Table 2.** Model comparison in the normalised pair space. The hard-gap entry is the best of 31 candidates; selection needs a 15 % improvement over the cone and $E_g \ge 1\,k_BT$.


| model | $E_g/k_BT$ | rms residual | ratio to cone | decision |
|---|---|---|---|---|
| ideal cone | 0.00 | 0.01563 | 1.00 | selected |
| best hard gap | 0.50 | 0.01970 | 1.26 | rejected |

**Why the gap loses.** A hard gap removes states within $E_g/2$ of the Dirac
point: it flattens $R_s$ near neutrality and sharpens the wings of $R_H$. The
measured $R_s$ peak is broad and smooth (Figure 5b), and the residual per
measurement is largest where the sign changes (Figure 5c) — exactly where a gap
would have to earn its improvement. The cone already reproduces the peak width; a gap
would cost a 26 % larger residual.

[[fig:3]]




**Uncertainty.** The bootstrap resamples one of the three repeats per index and
refits with the same library and rule, giving a median $E_F$ band half-width of
1.6 meV and a worst-case half-width of 14.9 meV near the end of the sweep; the
gap interval is $[0,0]$ $k_BT$ because no replicate selected one. The intervals describe stability against scatter, not model error: three repeats
cannot rule out systematic mis-modelling. And a
sub-thermal gap, $E_g<k_BT$, is indistinguishable from no gap at 300 K, because
the Fermi window smooths it away; the data cannot exclude one.

[[fig:4]]



**Device recommendation.** A gapless, symmetric cone with
$\mu\sim10^4$–$10^5$ cm$^2$ V$^{-1}$ s$^{-1}$ and a Fermi level that can be moved
by 0.22 eV is a semimetal, not a switch. It suits a transparent conductor, an
interconnect or a carrier-density sensor, where a high, weakly
temperature-dependent conductivity is an asset. It is a poor choice for a
switching device, because it has no thermally off state: the residual carrier
population at the Dirac point is set by $k_BT$ and cannot be removed by gating
alone.

[[fig:5]]








[[fig:6,7]]
## 4. L3 — where the wafer is non-uniform and whether it passes

**Question.** Where is the Hall-conductivity non-uniformity, what can the probe
resolve, and does the wafer pass the announced specification?

**Method.** The forward matrix [4] is $128\times100$ with rank 92, and every row sums
to less than $10^{-15}$, so a uniform offset is invisible to the probe and the
map must be constrained to zero mean. The rank is 92 rather than 100: eight directions are unconstrained, and the
near-null modes are flat, so a direct inverse amplifies them into a spurious
wafer-scale ramp. The reconstruction therefore
projects out the constant mode [5], $P = I - uu^{\mathsf T}$ with $u=\mathbf 1/\sqrt N$, and solves
$[P(A^{\mathsf T}A+\eta L^{\mathsf T}L)P + 10^{-9}I]\hat m = PA^{\mathsf T}\bar d$
with $L$ the $180\times100$ first-difference operator and the smoothness reference
$\eta_0 = 10^{-2}\lVert A\rVert_2^2/\lVert L\rVert_2^2 = 1.331\times10^{-3}$.
Sensitivity was checked over $\eta/\eta_0 = 0.01$ to 100. Features are the merged
connected components of the same-sign pixels above 30 % of the residual
amplitude, with neighbouring pixels merged rather than reported individually.
Resolution comes from injecting a zero-mean single-pixel feature (centre and
off-centre), forward-projecting with $A$ and reconstructing with the same $\eta$
and solver; the positive-lobe width gives FWHM $= 2.355\sigma$. The detection limit comes from
500 noise-only vectors drawn from the channel-wise repeat standard deviation and
propagated through the same solver (Figure 9).

[[fig:8]]




**Result.** The reconstruction reproduces the measured scan to within the visible linewidth
(Figure 11a); the residuals are discussed below. The zero-mean map has $\max|\hat m| = 3.58\,\%$ of the reference
conductivity, at $(x,y)=(-1.25,+1.89)$ probe pitches, with the opposite extremum
at $+2.94\,\%$ at $(+1.74,-1.59)$ (Figure 8a). The map is dominated by a plane:
$+0.59\,\%$ per pitch in $x$ and $-0.64\,\%$ per pitch in $y$, reaching
$\pm3.31\,\%$ at the corners. Removing that plane leaves a localised remainder
peaking at $-1.84\,\%$ over twelve merged pixels near $(-0.55,+1.80)$, with two
weaker positive lobes of $+0.93\,\%$ and $+0.69\,\%$ (Figure 8b, Table 3). The resolution
is 1.44 probe pitches at the central position and 1.30 at the off-centre one, so
1.44 is the conservative figure; the pixel pitch is 0.60 probe pitches, and the
point-spread function is a single-pixel cross (Figure 10a). The noise-only
ensemble gives $\delta_{95}=3.2\times10^{-6}$, i.e. $0.0003\,\%$ of the
reference conductivity (Figure 9d).

[[fig:9]]




**Table 3.** Merged features of the plane-removed map, in probe pitches and as a fraction of the reference conductivity. Neighbouring pixels are merged into one feature.

| feature | sign | amplitude (%) | x (pitch) | y (pitch) | pixels |
|---|---|---|---|---|---|
| A | negative | −1.84 | −0.55 | +1.80 | 12 |
| B | positive | +0.93 | −2.60 | +2.05 | 5 |
| C | positive | +0.69 | +2.10 | +2.57 | 4 |
| plane | – | ±3.31 at corners | – | – | all 100 |

**Decision.** With $a = \max|\hat m| = 3.58\,\%$ and $\delta_{95} = 0.0003\,\%$, the
decision envelope is $(3.578 \pm 0.0003)\,\%$ against a $3.0\,\%$ threshold. The
map is a **clear fail**: the shortfall of 0.58 percentage points is some two
thousand times the detection limit, so this is not a borderline call. The fail is
caused by the wafer-scale gradient, not by local defects: with the plane removed
the largest feature is $1.84\,\%$, comfortably inside the specification. The
process conclusion is therefore specific — the gradient across six probe pitches
is the yield limiter, and localised defects are already acceptable. The gradient
term alone reaches 3.31 % at the corners, above the threshold on its own, so the
specification is violated by the wafer-scale term independently of what the
defects do.






**Uncertainty and limits.** The regularisation scan (Figure 9a) is the crucial
check. Across $\eta/\eta_0 = 0.01$ to 1 the map amplitude changes by only 0.8 %
($3.608\,\%$ to $3.578\,\%$), and even at the over-smoothed end of the scan it
moves by 11 %, never near the threshold; the decision is therefore insensitive to
the regularisation. At the reference $\eta_0$ the data misfit is
$1.32\times10^{-4}$, ninety-six times the noise level of the three-repeat mean
($1.37\times10^{-6}$), which means $\eta_0$ over-smooths: at
$0.01\eta_0$ the misfit falls to $1.5$ times the noise and the amplitude moves by
0.8 %. The reported map therefore uses the reference $\eta_0$, and its amplitude is robust,
but it deliberately does not claim structures finer than 1.44 pitches, and the
tilt/localised decomposition is a descriptive device, not a model fitted by
maximum likelihood.

[[fig:10,11]]



## 5. Transfer: a printed polymer OFET

A printed polymer OFET uses the same three inferences but changes each model.
Its density of states is not a cone but a broadened distribution of
hopping and trap states, so occupancy — and hence the gate-voltage response — is
set by a Gaussian or exponential tail rather than by $k_BT$-wide thermal
smearing. The mobility extracted from a transfer curve uses the same Chapter 3 [2]
relation $\mu = 1/(en\rho)$, which is exactly why L1 matters: the carrier count
$n$ must come from the gate-charge model $n = C_i(V_G-V_T)/e$, not from a
band-edge integral, and contact resistance in series with the channel biases any
$\rho$ taken from the raw slope. L1's factor of 2.64 is therefore a warning, not
a number to reuse. L3 transfers almost directly: printed films vary
device-to-device, so a zero-mean uniformity map, a stated resolution in pixels
and a noise-linked detection limit are the right way to decide whether a coating
passes a specification, provided the gate-charge and contact models above are
handled first.

## 6. Conclusions

The three phases answer one question at three levels. L1 shows that the
extraction scale is a choice: at the measured operating point the band-edge
convention understates the carrier-referenced mobility and sensitivity by
$2.64\times$. L2 shows that the wafer is a gapless cone to within the
resolution of the data — the hard gap loses by 26 % in residual — with the
Fermi level drifting 0.22 eV and crossing neutrality at index 12, where the
Hall sign changes. L3 shows a clear fail of the 3.0 % specification (3.58 %),
caused by a wafer-scale gradient of 3.31 % rather than by local defects
(1.84 %), with a detection limit of $3.2\times10^{-6}$.

**Table 4.** The same pipeline on the regular and blind datasets.

| quantity | regular G15 | blind G15 |
|---|---|---|
| correction factor | 2.6408 | 4.3748 |
| DoS class | cone | cone |
| $E_F$ range (meV) | −71 to +146 | −81 to +135 |
| map maximum (%) | 3.58 | 4.42 |
| resolution (pitch) | 1.44 | 1.44 |
| decision | fail | fail |

[[fig:12]]



The main limitation is that none of these conclusions is checked against an
independent truth: the model class, the regularisation strength and the noise
estimate are all inferred from the same data they are used to interpret. The blind run of the identical pipeline (Table 4, Figure 12) is evidence that the
method transfers to fresh data, not evidence that it is correct.

## References

[1] Novoselov, K. S. *et al.* (2004) 'Electric field effect in atomically thin carbon films', *Science*, 306(5696), pp. 666–669.
[2] QXU6028 Chapter 3, *Carrier counting and mobility*, lecture notes, 2026–27.
[3] QXU6028 Chapter 5, *Reading the density of states from transport*, lecture notes, 2026–27.
[4] QXU6028 Chapter 6, *Probe measurements and uniformity*, lecture notes, 2026–27.
[5] Hansen, P. C. (1992) 'Analysis of discrete ill-posed problems by means of the L-curve', *SIAM Review*, 34(4), pp. 561–580.

## Figure captions

**Figure 1.** L1 carrier counting. (a) Correction factor across the sweep with the $C=2$ and $C=4$ crossings and the operating point. (b) The two finite-temperature counts.

**Figure 2.** L2 raw data: three repeats of the signed $R_H$ and of $R_{xx}$, with the pair of indices that brackets the sign change shaded.

**Figure 3.** L2 model library: (a) density of states of the cone and of a $2\,k_BT$ gap, with the removed states shaded, (b) the two Fermi windows, (c) model trajectories in the fit space with the measured pairs, (d) the L1 correction factor recomputed on the model grid.

**Figure 4.** L2 nearest-point fit in the separately normalised $(R_H,R_s)$ plane, coloured by acquisition index.

**Figure 5.** L2 channel overlays against the assigned $E_F$: (a) signed $\tilde R_H$, (b) $\tilde R_s$, (c) residual per measurement with its rms.

**Figure 6.** L2 Fermi-level trajectory with the bootstrap 16–84 % band and the sign-change index marked.

**Figure 7.** L2 model-selection evidence: (a) residual against gap size with the 15 % acceptance threshold, (b) per-index band width, (c) replicate model selection.

**Figure 8.** L3 zero-mean map: (a) full reconstruction with extrema marked, (b) after removing the fitted plane.

**Figure 9.** L3 method evidence: (a) misfit against regularisation, (b) singular-value spectrum and rank, (c) channel-wise repeat noise, (d) 500 noise-only reconstructions.

**Figure 10.** L3 resolution: point-spread function after injecting a single pixel at the centre (a) and off-centre (b), with the corresponding cross-sections (c, d).

**Figure 11.** L3 forward check: (a) measured and reconstructed readings, (b) residual against the $\pm3\sigma_j$ band.

**Figure 12.** Blind test: (a) the map reconstructed from the fresh dataset, (b) the gap-size scan for both datasets.
