function gaussian = JDHfixedT_3cmp_CORR_fun(COEF, rlist)

% Calculate the jump distance histogram associated (for a fixed time)
% associated to three species of diffusing molecules with diffusion
% coefficient D for A jumps.
% NOTE: correction for molecules going out of focus.

% Read Input

n1 = COEF(1);
n2 = COEF(2);
n3 = COEF(3);
D1 = COEF(4);
D2 = COEF(5);
D3 = COEF(6);


r = rlist(:,1);
t_bin = rlist(1,2);
dr = r(2) - r(1);
dZ = rlist(2,2);

n1_corr = corr_fraction(D1, n1, t_bin, dZ);
n2_corr = corr_fraction(D2, n2, t_bin, dZ);
n3_corr = corr_fraction(D3, n3, t_bin, dZ);

gaussian=dr.*r.*...
    (n1_corr/(2*D1*t_bin).*exp(-r.^2/(4*D1*t_bin)) + ...
 n2_corr/(2*D2*t_bin).*exp(-r.^2/(4*D2*t_bin)) + ...
 n3_corr/(2*D3*t_bin).*exp(-r.^2/(4*D3*t_bin)));

end

function n_corr = corr_fraction(D,n,t,dz)

n_corr=n/(2*dz).*(2*dz.*erf(dz./sqrt(D.*t)) + sqrt(4*D.*t./pi).*(exp(-dz^2./(D*t)) -1));

end