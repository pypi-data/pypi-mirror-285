function [COEF,fit, COEFsigma] = JDHfixedT_3cmp_CORR_fit(Hist,jumpTime, D0s, dZ)

% JDHfixedT_3cmp_fit
% -------------------------------------------------------------------------
% This function calls the fitting routine for the fit of a jump histogram
% (fixed time). The fitting is performed with the lsqnonlin function from
% from the optimization toolbox. The function is a three-component diffusion
% model. NOTE: correction for molecules going out of focus.
% [Aug-2022: fitting the Cumulative distribution instead of the PDF by 
% minimizing the cumulative squared sum of residuals]
% -------------------------------------------------------------------------
% The output COEF has the resulting parameters of the fit in the order
% [n1, n2, n3, D1, D2, D3, SSR];
% The output fit is a two column vector: fit(:,1) =rlist
%                                        fit(:,2) = actual fit



% Read Input
rlist(:,1) = Hist(:,1);
rlist(1,2)=jumpTime;
rlist(2,2) = dZ;

Y = Hist(:,2);

% define initial values for the parameters
COEF0 = [.33*sum(Y),0.33*sum(Y), 0.33*sum(Y) D0s(1), D0s(2) D0s(3)];


% define lower boundaries for the fitted parameters
COEF_LB = [0, 0, 0, 0, 0, 0];

% define upper boundaries for the fitted parameters
COEF_UB = [sum(Y), sum(Y), 2*sum(Y), Inf, Inf, Inf];

% Define anonymous function for the fitting
fitfun = @(COEF) cumsum(JDHfixedT_3cmp_CORR_fun(COEF, rlist) - Y);



% Define options for the fitting function
options = optimset('FunValCheck','off','Display','off');

% run fitting routine
[COEF, resNorm, residuals,exitflag,output,lambda,jacobian]= lsqnonlin(fitfun,COEF0,COEF_LB,COEF_UB,options);
ci = nlparci(COEF,residuals,'jacobian',jacobian);
COEFsigma = (ci(:,2) - ci(:,1))/2;
COEFsigma = COEFsigma';

% check if the fit provides acceptable estimates
if min(COEF > 0) == 1 && max(COEF)< Inf
    fit(:,1)=rlist(:,1);
    fit(:,2)=JDHfixedT_3cmp_CORR_fun(COEF,rlist);
    
else % Otherwise put the fit to 0
    fit= zeros(length(rlist(:,1)),2);
    disp('THREE COMPONENT FIT of JDH1 FAILED!')
end


%calculate SSR on Cumulative distribution. 
CDF_res = cumsum(fit(:,2)-Hist(:,2));
SSR = sum(CDF_res.^2);

%SSR = sum((fit(:,2)-Hist(:,2)).^2);


% Sort Coefficients and fractions
[tmp, idx] = sort(COEF(4:6));
COEF = [COEF(idx), tmp];


disp('')
disp('--------------------------------------------')
disp('Three component Fit of FJH')
disp(['fitted D1 = ', num2str(COEF(4)), ' mum^2/s'])
disp(['fitted D2 = ', num2str(COEF(5)), ' mum^2/s'])
disp(['fitted D3 = ', num2str(COEF(6)), ' mum^2/s'])
disp(['fitted f1 = ', num2str(COEF(1)/(COEF(1)+COEF(2)+COEF(3)))])
disp(['fitted f2 = ', num2str(COEF(2)/(COEF(1)+COEF(2)+COEF(3)))])
disp(['fitted f3 = ', num2str(COEF(3)/(COEF(1)+COEF(2)+COEF(3)))])
disp(['SSR = ', num2str(SSR)]);
disp('--------------------------------------------')
disp('')

COEF(7) = SSR;
