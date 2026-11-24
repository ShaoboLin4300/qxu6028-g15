# Critical self-assessment (150–200 words) — group G15

The weakest part of the analysis is the regularisation strength in L3. We used
the Guide reference η₀ and only a five-point scan, then discovered that the
resulting map leaves a data misfit ninety-six times the repeat noise. That means
the reported map is over-smoothed: features between 0.6 and 1.44 probe pitches
are present in the data but are not resolved, so our feature amplitudes are lower
bounds. A credible remedy is to choose η by the discrepancy principle — the
largest η whose misfit matches the noise of the three-repeat mean — and to
validate the choice on a synthetic map with known feature positions, where the
true map error can be measured rather than assumed.

The second weakness is the uncertainty budget in L2. The bootstrap resamples only
three repeats per index, so the reported Fermi-level band (1.6 meV median)
describes repeat scatter, not model error; the gap interval is formally [0, 0]
k_BT because no replicate selected a gap, which overstates confidence. A
parametric bootstrap from the fitted model, together with an interval that
marginalises over the cone and hard-gap families, would give an honest spread.
