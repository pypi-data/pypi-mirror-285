function gaussian = JDHfixedT_1cmp_CORR_fun(COEF, rlist)

% Calculate the jump distance histogram associated (for a fixed time)
% associated to three species of diffusing molecules with diffusion
% coefficient D for A jumps.
% NOTE: correction for molecules going out of focus.

% Read Input

n1 = COEF(1);
D1 = COEF(2);



r = rlist(:,1);
t_bin = rlist(1,2);
dr = r(2) - r(1);
dZ = rlist(2,2);

n1_corr = corr_fraction(D1, n1, t_bin, dZ);



gaussian=dr.*r.*...
    (n1_corr/(2*D1*t_bin).*exp(-r.^2/(4*D1*t_bin)));

end

function n_corr = corr_fraction(D,n,t,dz)

n_corr=n*(2*dz).*(2*dz.*erf(dz./sqrt(D.*t)) + sqrt(4*D.*t./pi).*(exp(-dz^2./(D*t)) -1));

end