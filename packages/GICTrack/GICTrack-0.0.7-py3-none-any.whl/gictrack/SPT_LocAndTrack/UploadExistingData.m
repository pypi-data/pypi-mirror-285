%   SerialProcess_PALM_JF549.m
%   Anders Sejr Hansen, August 2016
%   Yew Yan Wong, March 2022
%   clear; clc; close all; clearvars -global

%   DESCRIPTION
%   This script takes as input a folder with tiff files and then outputs
%   workspaces with tracked single molecules. Briefly, it uses the
%   BioFormats package to read in nd2 files. Next, the script feeds the
%   images as a 3D matrix into the localization part of the MTT algorithm
%   (Part 1) and subsequently, the tracked particles are fed into the
%   tracking part of the MTT algorithm (Part 2). 

%%%%%%%%%%%%%%%%%%%% DEFINE INPUT AND OUTPUT PATHS %%%%%%%%%%%%%%%%%%%%%%%%
% add the neccesary paths:
addpath(genpath(['.' filesep 'Batch_MTT_code' filesep])); % MTT & BioFormats
addpath(genpath(['.' filesep 'CMP_Fit' filesep])); % Component fittings
disp('added paths for MTT algorithm mechanics, bioformats...');

load([matLoc, '/tifupload.mat']);
runParallel = false;

if iscell(file_names)
  Filenames = file_names;
else
  Filenames = cell(1,1);
  Filenames{1} = file_names;
end
% Check if the user's machine has the number of cores they desired to use
if numCores > feature('numcores')
  %   reduce the cores to use to the machine's maximum number of cores
  numCores = feature('numcores');
end
if numCores == 1 || length(Filenames) == 1
  runParallel = false;
end

%% Create list of tracked files uploaded
tracked_files = cell(numel(Filenames), 1);
for n = 1 : numel(Filenames)
  tracked_files{n} = Filenames{n};
end

%% QC
rejectedFiles = cell(0); files_to_remove = cell(length(tracked_files), 1);
for iter = 1 : length(tracked_files)
  load([input_path, tracked_files{iter}]);
  save([output_path, tracked_files{iter}, '_Tracked.mat'], 'trackedPar');
  
  if length(trackedPar) < min_traj
    rejectedFiles{end+1} = tracked_files{iter};
    files_to_remove{iter} = 1;
    continue
  end
  % trackedPar to tracks
  tracks = struct('data', []);
  for n = 1 : numel(trackedPar)
    tracks(n) = struct('data', [reshape(trackedPar(n).TimeStamp, [], 1), trackedPar(n).xy]);
  end
  
  rows_to_remove = [];
  for n = 1 : numel(tracks)
    if size(tracks(n).data, 1) < traj_length
      rows_to_remove = [rows_to_remove; n];
    end
  end
  tracks(rows_to_remove) = [];
  if isempty(tracks)
    rejectedFiles{end+1} = tracked_files{iter};
    files_to_remove{iter} = 1;
    continue
  end
end
tracked_files(~cellfun(@isempty, files_to_remove)) = [];
Filenames = tracked_files';
save([output_path_further_processing, 'acceptedFiles.mat'], 'Filenames');
save([output_path_further_processing, 'rejectedFiles.mat'], 'rejectedFiles');
%% Producing slow acquisition data
if acquisition_rate == "slow"
  for k = 1:numel(file_names)
    load([input_path, tracked_files{k}]);
    txt = [];
    for n = 1 : length(trackedPar)
      txt = [txt; trackedPar(n).xy trackedPar(n).Frame repelem(n, length(trackedPar(n).Frame))'];
    end
    fnm = fullfile([output_path_further_processing, file_names{k}, '_table.txt']);
%     txt = importdata(fnm);
    index = unique(txt(:,4));
    [p,~] = size(index);

    tracklength = zeros(p, 1);
    for i=1:p
      logi=find(txt(:,4)==index(i));
      tracklength(i) = (txt(logi(end),3)-txt(logi(1),3)+1);
    end
    tracklength = (ExposureTime / 1000) * tracklength;
    writematrix(tracklength', [fnm(1:end-4) '_dwelltime.txt'], 'delimiter', '\t');
    a = tracklength;
    binsize = 1;
    binwindows = 0:binsize:1000;
    [n,~]=hist(a,binwindows);
    cdf_n = [sum(n), sum(n) - cumsum(n)]/sum(n);
    logind=find(cdf_n>0.01);
    binwindows = 0:binsize:(logind(end)+1)*binsize;
    [n,xout]=hist(a,binwindows);
    histogram(a, binwindows);
    %   hist(a,binwindows);
    cdf_n = [sum(n), sum(n) - cumsum(n)]/sum(n);
    cdf_n=cdf_n(1:end-1);

    % xout is the time, n is the count.
    % Please define the bleach rate (unit in second) from previsous measurement
    myfun = @(x) cdf_n(1:end) - x(1) - x(2)*exp(-xout(1:end)/x(3));%1-component fitting
    myfun2 = @(r) cdf_n - r(1)*exp(-xout/r(2))-(1-r(1))*exp(-xout/r(3));%2-component fitting
    x0=[0.05, 1, 5];
    r0=[0.5,8,1.2];
    options = optimset('Algorithm',{'levenberg-marquardt',0.000001});
    x=lsqnonlin(myfun,x0,[],[],options);
    r=lsqnonlin(myfun2,r0,[],[],options);
    figure;
    hold on
    plot(xout, cdf_n,'o');
    xfit=xout(1):0.9:max(xout);
    yfit= x(1) + x(2)*exp(-xfit/x(3));
    plot(xfit,yfit,'-r');
    title('1-Component Fitting', 'interpreter', 'latex');
    hold off
    f1=figure;
    hold on
    plot(xout, cdf_n,'o');
    xfit=0:0.9:max(xout);
    yfit= r(1)*exp(-xfit/r(2))+(1-r(1))*exp(-xfit/r(3));
    plot(xfit,yfit,'-r')
    a = r(1);
    %   b = r(2);
    c = r(3);
    TrueR = (bleach_rate - 1)/(bleach_rate/x(3) -1);
    TrueR2 = (bleach_rate - 1)/(bleach_rate/max(r(2),r(3)) -1);
    title('2-Components Fitting', 'interpreter', 'latex');
    polyfit_str = ['R1= ' num2str(TrueR2) ' Fraction= ' num2str(a)...
      'R2= ' num2str(c)];
    text(1,1,polyfit_str,'FontSize',18);

    saveas(f1,strcat(fnm, "_fig", ".tif"));

    fprintf('The residence time is %d before correction of one-component fitting.\n', x(3));
    fprintf('The true residence time is %d of one component fitting after correction.\n', TrueR);
    fprintf('The residence time are %d and %d with fraction %d of two-components fitting.\n', r(2),r(3),r(1));
    fprintf('The true residence time is %d of two components fitting after correction.\n', TrueR2);

    clear tracklength;

    full_row = {fnm TrueR2 c a};
    df = full_row;
    if k == 1
      df_final = df;
    else
      df_final =[df_final;df];
    end

    dwellTimeData = [TrueR2, c, a];
    save([output_path, file_names{k}, '_dwellTime.mat'], 'dwellTimeData');

  end

%   % Convert cell to a table and use first row as variable names
%   T = cell2table(df_final);
% 
%   % Write the table to a CSV file
%   writetable(T,[pathname 'LongDwell_data.csv']);
end

%% Producing diffusion data
subPlotNumbers = ceil(sqrt(length(tracked_files)));
Filenames = tracked_files;
figure;
if runParallel
  % if there's less files to run than number of cores, reduce the core to use even further
  p = gcp('nocreate');
  if isempty(p)
    parpool('local', min([numCores, length(Filenames)]));
  end
  parfor iter = 1:length(tracked_files)
    maxJump = 0;
    data = load([input_path, tracked_files{iter}, '.mat']);
    trackedPar = data.trackedPar;
    try
      settings = data.settings;
    catch
      settings = 0;
    end
    parsave([output_path, tracked_files{iter}, '_Tracked.mat'], trackedPar, settings);

    % trackedPar to tracks
    tracks = struct('data', []);
    for n = 1 : numel(trackedPar)
      tracks(n) = struct('data', [trackedPar(n).TimeStamp, trackedPar(n).xy]);
    end

    rows_to_remove = [];
    for n = 1 : numel(tracks)
      if size(tracks(n).data, 1) < traj_length
        rows_to_remove = [rows_to_remove; n];
      end
    end
    tracks(rows_to_remove) = [];

    msd = computeMSD(tracks, tol);
    lfit = fitMSD(msd, clip_factor, analysis_type);

    subplot(subPlotNumbers, subPlotNumbers, iter);
    hist(log10(lfit.a(lfit.a>0)), 15);
    title(Filenames{iter}, 'interpreter', 'none');
    xlabel('Log10(D(um2/s)', 'interpreter', 'latex');
    ylabel('Counts', 'interpreter', 'latex');

    D = log10(lfit.a(lfit.a>0));
    E = lfit.a(lfit.a>0);

    tracks = tracks(lfit.a>0);
    msd = msd(lfit.a>0);
    dataTraj = [];
    dataTrack = [];
    dataAngle = [];
    for n = 1 : numel(tracks)
      traj_size = size(tracks(n).data, 1);
      trackData = tracks(n).data;
      v1 = [trackData(2 : size(trackData, 1) - 1, 2), trackData(2 : size(trackData, 1) - 1, 3), 0 * (2 : size(trackData, 1) - 1)'] - ...
        [trackData(1 : size(trackData, 1) - 2, 2), trackData(1 : size(trackData, 1) - 2, 3), 0 * (1 : size(trackData, 1) - 2)'];
      v2 = [trackData(3 : size(trackData, 1), 2), trackData(3 : size(trackData, 1), 3), 0 * (3 : size(trackData, 1))'] - ...
        [trackData(2 : size(trackData, 1) - 1, 2), trackData(2 : size(trackData, 1) - 1, 3), 0 * (2 : size(trackData, 1) - 1)'];
      dist = pdist(tracks(n).data(:, 2:3));
      Theta = atan2(vecnorm(cross(v1, v2, 2), size(v1, 1), 2), dot(v1, v2, 2));
      dataAngle = [dataAngle; n, histcounts(Theta, deg2rad([0:10:180]))];
      dataTraj = [dataTraj; convertCharsToStrings(Filenames{iter}), n, traj_size, mean(msd{n}(1 : traj_size, 2), 'omitnan'), D(n), tracks(n).data(1,1), tracks(n).data(end,1)];
      %     dataTrack = [dataTrack; repelem(n, traj_size)', tracks(n).data, msd{n}(1 : traj_size, 2)];
%       dataTrack = [dataTrack; repelem(n, traj_size)', tracks(n).data, msd{n}(1 : traj_size, 2), [0, dist(2:traj_size)]', [zeros(traj_size - length(Theta), 1); Theta]];
      dataTrack = [dataTrack; repelem(n, traj_size)', tracks(n).data(:, 1:3), msd{n}(1 : traj_size, 2), [0, dist(2:traj_size)]', [zeros(traj_size - length(Theta), 1); Theta], repelem(0, traj_size)', repelem(0, traj_size)'];
    end
    dataTraj = cellstr(dataTraj);
    parsaveangle([output_path, Filenames{iter}], dataAngle, dataTraj, dataTrack, E, msd)

    % Jump distance computation
    trackedPar(rows_to_remove) = [];
    trackedPar = trackedPar(lfit.a>0);
    jdTracks = [];
    for n = 1 : numel(trackedPar)
      %     jdTracks = [jdTracks; tracks(n).xy, tracks(n).Frame, repelem(n, length(tracks(n).Frame))', repelem(D(n), length(tracks(n).Frame))'];
      jdTracks = [jdTracks; trackedPar(n).xy, trackedPar(n).Frame, repelem(n, length(trackedPar(n).Frame))', repelem(D(n), length(trackedPar(n).Frame))'];
      if length(trackedPar(n).Frame) > maxJump
        maxJump = length(trackedPar(n).Frame);
      end
    end
%     binEdges = 0 : ExposureTime / 1000 : maxJump;
    binEdges = 0 : 0.02 : 2; % expected longest distance travelled
    maxJump = 1;
    [tlist, rlist, JDH] = calculateJDH(jdTracks, maxJump, binEdges, ExposureTime / 1000, clip_factor, analysis_type, 0, 0);
    % Isolate first histogram of displacements;
    FJH = [];
    FJH(:,1) = rlist;
    FJH(:,2) = JDH(1,:); % only maxFrame = 1 is used
    %   FJH(:, 2) = sum(JDH, 1);
    D0 = 0.1;
    deltaZ = 1;

    % Fit first histogram of displacements;
%     [FJH_Coef1Cmp,FJH_Fit1Cmp,FJH_Sigma1Cmp] = JDHfixedT_1cmp_fit(FJH, ExposureTime / 1000, D0);
%     [FJH_Coef2Cmp,FJH_Fit2Cmp, FJH_Sigma2Cmp] = JDHfixedT_2cmp_fit(FJH, ExposureTime / 1000, [10*D0, D0]);
%     [FJH_Coef3Cmp,FJH_Fit3Cmp, FJH_Sigma3Cmp] = JDHfixedT_3cmp_fit(FJH, ExposureTime / 1000, [10*D0, D0, 0.1*D0]);
    [FJH_Coef1Cmp,FJH_Fit1Cmp, FJH_Sigma1Cmp] = JDHfixedT_1cmp_CORR_fit(FJH, ExposureTime / 1000, D0, deltaZ/2);
    [COEF_2,FJH_Fit2Cmp, FJH_Sigma2Cmp] = JDHfixedT_2cmp_CORR_fit(FJH, ExposureTime / 1000, [D0 10*D0], deltaZ/2);
    [COEF_3,FJH_Fit3Cmp, FJH_Sigma3Cmp] = JDHfixedT_3cmp_CORR_fit(FJH, ExposureTime / 1000, [D0/10, D0, 10*D0], deltaZ/2);

    % Add fits of first histogram of displeacements to FJH.
    FJH(:,3) = FJH_Fit1Cmp(:,2);
    FJH(:,4) = FJH_Fit2Cmp(:,2);
    FJH(:,5) = FJH_Fit3Cmp(:,2);

    rlist(1,2) =tlist(1);

    FJH_Coef2Cmp = [sum(COEF_2(1:2)), COEF_2(3:4), COEF_2(1) / sum(COEF_2(1:2)), COEF_2(5)];
    FJH_Coef3Cmp = [sum(COEF_3(1:3)), COEF_3(4:6), COEF_3(1) / sum(COEF_3(1:3)), COEF_3(2) / sum(COEF_3(1:3)), COEF_3(7)];

    FitPar = [FJH_Coef1Cmp, FJH_Coef2Cmp, FJH_Coef3Cmp;...
      FJH_Sigma1Cmp, 0, FJH_Sigma2Cmp, 0, FJH_Sigma3Cmp, 0];

    % Two component diffusion fit
    FirstCMP = ...
      JDHfixedT_1cmp_fun([FitPar(1,4)* FitPar(1,7), FitPar(1,5)],rlist);
    SecondCMP = ...
      JDHfixedT_1cmp_fun([FitPar(1,4)* (1 - FitPar(1,7)), FitPar(1,6)],rlist);
    twoCMPFit = [FirstCMP, SecondCMP];

    % Three component diffusion fit
    FirstCMP = ...
      JDHfixedT_1cmp_fun([FitPar(1,9)* FitPar(1,13), FitPar(1,10)],rlist);
    SecondCMP = ...
      JDHfixedT_1cmp_fun([FitPar(1,9)* FitPar(1,14), FitPar(1,11)],rlist);
    ThirdCMP = JDHfixedT_1cmp_fun...
      ([FitPar(1,9)* (1 - FitPar(1,13) - FitPar(1,14)), FitPar(1,12)],rlist);
    threeCMPFit = [FirstCMP, SecondCMP, ThirdCMP];

    parsavedata([output_path, Filenames{iter}], FJH, FitPar, twoCMPFit, threeCMPFit);
  end
else
  for iter = 1:length(tracked_files)
    maxJump = 0;
    load([input_path, tracked_files{iter}, '.mat']);
    save([output_path, tracked_files{iter}, '_Tracked.mat'], 'trackedPar');

    % trackedPar to tracks
    tracks = struct('data', []);
    for n = 1 : numel(trackedPar)
      tracks(n) = struct('data', [trackedPar(n).TimeStamp, trackedPar(n).xy]);
    end

    rows_to_remove = [];
    for n = 1 : numel(tracks)
      if size(tracks(n).data, 1) < traj_length
        rows_to_remove = [rows_to_remove; n];
      end
    end
    tracks(rows_to_remove) = [];

    msd = computeMSD(tracks, tol);
    lfit = fitMSD(msd, clip_factor, analysis_type);

    subplot(subPlotNumbers, subPlotNumbers, iter);
    hist(log10(lfit.a(lfit.a>0)), 15);
    title(Filenames{iter}, 'interpreter', 'none');
    xlabel('Log10(D(um2/s)', 'interpreter', 'latex');
    ylabel('Counts', 'interpreter', 'latex');

    D = log10(lfit.a(lfit.a>0));
    E = lfit.a(lfit.a>0);

    tracks = tracks(lfit.a>0);
    msd = msd(lfit.a>0);
    dataTraj = [];
    dataTrack = [];
    dataAngle = [];
    for n = 1 : numel(tracks)
      traj_size = size(tracks(n).data, 1);
      trackData = tracks(n).data;
      v1 = [trackData(2 : size(trackData, 1) - 1, 2), trackData(2 : size(trackData, 1) - 1, 3), 0 * (2 : size(trackData, 1) - 1)'] - ...
        [trackData(1 : size(trackData, 1) - 2, 2), trackData(1 : size(trackData, 1) - 2, 3), 0 * (1 : size(trackData, 1) - 2)'];
      v2 = [trackData(3 : size(trackData, 1), 2), trackData(3 : size(trackData, 1), 3), 0 * (3 : size(trackData, 1))'] - ...
        [trackData(2 : size(trackData, 1) - 1, 2), trackData(2 : size(trackData, 1) - 1, 3), 0 * (2 : size(trackData, 1) - 1)'];
      dist = pdist(tracks(n).data(:, 2:3));
      Theta = atan2(vecnorm(cross(v1, v2, 2), size(v1, 1), 2), dot(v1, v2, 2));
      dataAngle = [dataAngle; n, histcounts(Theta, deg2rad([0:10:180]))];
      dataTraj = [dataTraj; convertCharsToStrings(Filenames{iter}), n, traj_size, mean(msd{n}(1 : traj_size, 2), 'omitnan'), D(n), tracks(n).data(1,1), tracks(n).data(end,1)];
      %     dataTrack = [dataTrack; repelem(n, traj_size)', tracks(n).data, msd{n}(1 : traj_size, 2)];
%       dataTrack = [dataTrack; repelem(n, traj_size)', tracks(n).data, msd{n}(1 : traj_size, 2), [0, dist(2:traj_size)]', [zeros(traj_size - length(Theta), 1); Theta]];
      dataTrack = [dataTrack; repelem(n, traj_size)', tracks(n).data(:, 1:3), msd{n}(1 : traj_size, 2), [0, dist(2:traj_size)]', [zeros(traj_size - length(Theta), 1); Theta], repelem(0, traj_size)', repelem(0, traj_size)'];
    end
    dataTraj = cellstr(dataTraj);
    save([output_path, Filenames{iter}, '_dataAngle.mat'], 'dataAngle');
    save([output_path, Filenames{iter}, '_dataTraj.mat'], 'dataTraj');
    save([output_path, Filenames{iter}, '_dataTrack.mat'], 'dataTrack');

    %   save([output_path, Filenames{iter}, '_Log_Diffusion.mat'], 'D');
    save([output_path, Filenames{iter}, '_Diffusion.mat'], 'E');
    save([output_path, Filenames{iter}, '_msd.mat'], 'msd');

    % Jump distance computation
    trackedPar(rows_to_remove) = [];
    trackedPar = trackedPar(lfit.a>0);
    jdTracks = [];
    for n = 1 : numel(trackedPar)
      %     jdTracks = [jdTracks; tracks(n).xy, tracks(n).Frame, repelem(n, length(tracks(n).Frame))', repelem(D(n), length(tracks(n).Frame))'];
      jdTracks = [jdTracks; trackedPar(n).xy, trackedPar(n).Frame, repelem(n, length(trackedPar(n).Frame))', repelem(D(n), length(trackedPar(n).Frame))'];
      if length(trackedPar(n).Frame) > maxJump
        maxJump = length(trackedPar(n).Frame);
      end
    end
%     binEdges = 0 : ExposureTime / 1000 : maxJump;
    binEdges = 0 : 0.02 : 2; % expected longest distance travelled
    maxJump = 1;
    [tlist, rlist, JDH] = calculateJDH(jdTracks, maxJump, binEdges, ExposureTime / 1000, clip_factor, analysis_type, 0, 0);
    % Isolate first histogram of displacements;
    FJH = [];
    FJH(:,1) = rlist;
    FJH(:,2) = JDH(1,:); % only maxFrame = 1 is used
    %   FJH(:, 2) = sum(JDH, 1);
    D0 = 0.1;
    deltaZ = 1;

    % Fit first histogram of displacements;
%     [FJH_Coef1Cmp,FJH_Fit1Cmp,FJH_Sigma1Cmp] = JDHfixedT_1cmp_fit(FJH, ExposureTime / 1000, D0);
%     [FJH_Coef2Cmp,FJH_Fit2Cmp, FJH_Sigma2Cmp] = JDHfixedT_2cmp_fit(FJH, ExposureTime / 1000, [10*D0, D0]);
%     [FJH_Coef3Cmp,FJH_Fit3Cmp, FJH_Sigma3Cmp] = JDHfixedT_3cmp_fit(FJH, ExposureTime / 1000, [10*D0, D0, 0.1*D0]);
    [FJH_Coef1Cmp,FJH_Fit1Cmp, FJH_Sigma1Cmp] = JDHfixedT_1cmp_CORR_fit(FJH, ExposureTime / 1000, D0, deltaZ/2);
    [COEF_2,FJH_Fit2Cmp, FJH_Sigma2Cmp] = JDHfixedT_2cmp_CORR_fit(FJH, ExposureTime / 1000, [D0 10*D0], deltaZ/2);
    [COEF_3,FJH_Fit3Cmp, FJH_Sigma3Cmp] = JDHfixedT_3cmp_CORR_fit(FJH, ExposureTime / 1000, [D0/10, D0, 10*D0], deltaZ/2);

    % Add fits of first histogram of displeacements to FJH.
    FJH(:,3) = FJH_Fit1Cmp(:,2);
    FJH(:,4) = FJH_Fit2Cmp(:,2);
    FJH(:,5) = FJH_Fit3Cmp(:,2);

    rlist(1,2) =tlist(1);

    FJH_Coef2Cmp = [sum(COEF_2(1:2)), COEF_2(3:4), COEF_2(1) / sum(COEF_2(1:2)), COEF_2(5)];
    FJH_Coef3Cmp = [sum(COEF_3(1:3)), COEF_3(4:6), COEF_3(1) / sum(COEF_3(1:3)), COEF_3(2) / sum(COEF_3(1:3)), COEF_3(7)];

    FitPar = [FJH_Coef1Cmp, FJH_Coef2Cmp, FJH_Coef3Cmp;...
      FJH_Sigma1Cmp, 0, FJH_Sigma2Cmp, 0, FJH_Sigma3Cmp, 0];

    % Two component diffusion fit
    FirstCMP = ...
      JDHfixedT_1cmp_fun([FitPar(1,4)* FitPar(1,7), FitPar(1,5)],rlist);
    SecondCMP = ...
      JDHfixedT_1cmp_fun([FitPar(1,4)* (1 - FitPar(1,7)), FitPar(1,6)],rlist);
    twoCMPFit = [FirstCMP, SecondCMP];

    % Three component diffusion fit
    FirstCMP = ...
      JDHfixedT_1cmp_fun([FitPar(1,9)* FitPar(1,13), FitPar(1,10)],rlist);
    SecondCMP = ...
      JDHfixedT_1cmp_fun([FitPar(1,9)* FitPar(1,14), FitPar(1,11)],rlist);
    ThirdCMP = JDHfixedT_1cmp_fun...
      ([FitPar(1,9)* (1 - FitPar(1,13) - FitPar(1,14)), FitPar(1,12)],rlist);
    threeCMPFit = [FirstCMP, SecondCMP, ThirdCMP];

    save([output_path, Filenames{iter}, '_CMPFitPar.mat'], 'FJH');
    save([output_path, Filenames{iter}, '_FitPar.mat'], 'FitPar');
    save([output_path, Filenames{iter}, '_2CMPFit.mat'], 'twoCMPFit');
    save([output_path, Filenames{iter}, '_3CMPFit.mat'], 'threeCMPFit');
  end
end
sgtitle('Diffusion Coefficient for all population', 'interpreter', 'latex');

% figure;
% for iter = 1:length(tracked_files)
%   maxJump = 0;
%   
%   load([input_path, tracked_files{iter}]);
%   save([output_path, tracked_files{iter}, '_Tracked.mat'], 'trackedPar');
%   
%   % trackedPar to tracks
%   tracks = struct('data', []);
%   for n = 1 : numel(trackedPar)
%     tracks(n) = struct('data', [reshape(trackedPar(n).TimeStamp, [], 1), trackedPar(n).xy]);
%   end
%   
%   rows_to_remove = [];
%   for n = 1 : numel(tracks)
%     if size(tracks(n).data, 1) < traj_length
%       rows_to_remove = [rows_to_remove; n];
%     end
%   end
%   tracks(rows_to_remove) = [];
%   
%   msd = computeMSD(tracks, tol);
%   lfit = fitMSD(msd, clip_factor, analysis_type);
%   
%   subplot(subPlotNumbers, subPlotNumbers, iter);
%   hist(log10(lfit.a(lfit.a>0)), 15);
%   title(Filenames{iter}, 'interpreter', 'none');
%   xlabel('Log10(D(um2/s)', 'interpreter', 'latex');
%   ylabel('Counts', 'interpreter', 'latex');
%   
%   D = log10(lfit.a(lfit.a>0));
%   E = lfit.a(lfit.a>0);
% 
%   tracks = tracks(lfit.a>0);
%   msd = msd(lfit.a>0);
%   dataTraj = [];
%   dataTrack = [];
%   dataAngle = [];
%   for n = 1 : numel(tracks)
%     traj_size = size(tracks(n).data, 1);
%     trackData = tracks(n).data;
%     v1 = [trackData(2 : size(trackData, 1) - 1, 2), trackData(2 : size(trackData, 1) - 1, 3), 0 * (2 : size(trackData, 1) - 1)'] - ...
%          [trackData(1 : size(trackData, 1) - 2, 2), trackData(1 : size(trackData, 1) - 2, 3), 0 * (1 : size(trackData, 1) - 2)'];
%     v2 = [trackData(3 : size(trackData, 1), 2), trackData(3 : size(trackData, 1), 3), 0 * (3 : size(trackData, 1))'] - ...
%          [trackData(2 : size(trackData, 1) - 1, 2), trackData(2 : size(trackData, 1) - 1, 3), 0 * (2 : size(trackData, 1) - 1)'];
%     dist = pdist(tracks(n).data(:, 2:3));
%     Theta = atan2(vecnorm(cross(v1, v2, 2), size(v1, 1), 2), dot(v1, v2, 2));
%     dataAngle = [dataAngle; n, histcounts(Theta, deg2rad([0:10:180]))];
%     dataTraj = [dataTraj; convertCharsToStrings(Filenames{iter}), n, traj_size, mean(msd{n}(1 : traj_size, 2), 'omitnan'), D(n), tracks(n).data(1,1), tracks(n).data(end,1)];
% %     dataTrack = [dataTrack; repelem(n, traj_size)', tracks(n).data, msd{n}(1 : traj_size, 2)];
%     dataTrack = [dataTrack; repelem(n, traj_size)', tracks(n).data, msd{n}(1 : traj_size, 2), [0, dist(2:traj_size)]', [zeros(traj_size - length(Theta), 1); Theta]];
%   end
%   dataTraj = cellstr(dataTraj);
%   save([output_path, Filenames{iter}, '_dataAngle.mat'], 'dataAngle');
%   save([output_path, Filenames{iter}, '_dataTraj.mat'], 'dataTraj');
%   save([output_path, Filenames{iter}, '_dataTrack.mat'], 'dataTrack');
%   
% %   save([output_path, Filenames{iter}, '_Log_Diffusion.mat'], 'D');
%   save([output_path, Filenames{iter}, '_Diffusion.mat'], 'E');
%   save([output_path, Filenames{iter}, '_msd.mat'], 'msd', '-v7.3');
% 
%   % Jump distance computation
%   trackedPar(rows_to_remove) = [];
%   trackedPar = trackedPar(lfit.a>0);
%   jdTracks = [];
%   for n = 1 : numel(trackedPar)
% %     jdTracks = [jdTracks; tracks(n).xy, tracks(n).Frame, repelem(n, length(tracks(n).Frame))', repelem(D(n), length(tracks(n).Frame))'];
%     jdTracks = [jdTracks; trackedPar(n).xy, reshape(trackedPar(n).Frame, [], 1), repelem(n, length(trackedPar(n).Frame))', repelem(D(n), length(trackedPar(n).Frame))'];
%     if length(trackedPar(n).Frame) > maxJump
%       maxJump = length(trackedPar(n).Frame);
%     end
%   end
%   binEdges = 0 : ExposureTime / 1000 : maxJump;
%   [tlist, rlist, JDH] = calculateJDH(jdTracks, 1, binEdges, ExposureTime / 1000, clip_factor, analysis_type, 0, 0);
%   % Isolate first histogram of displacements;
%   FJH = [];
%   FJH(:,1) = rlist;
%   FJH(:,2) = JDH(1,:); % only maxFrame = 1 is used
%   D0 = 0.1;
%   deltaZ = 1;
% 
%   % Fit first histogram of displacements;
% %   [FJH_Coef1Cmp,FJH_Fit1Cmp,FJH_Sigma1Cmp] = JDHfixedT_1cmp_fit(FJH, ExposureTime / 1000, D0);
% %   [FJH_Coef2Cmp,FJH_Fit2Cmp, FJH_Sigma2Cmp] = JDHfixedT_2cmp_fit(FJH, ExposureTime / 1000, [10*D0, D0]);
% %   [FJH_Coef3Cmp,FJH_Fit3Cmp, FJH_Sigma3Cmp] = JDHfixedT_3cmp_fit(FJH, ExposureTime / 1000, [10*D0, D0, 0.1*D0]);
%   [FJH_Coef1Cmp,FJH_Fit1Cmp, FJH_Sigma1Cmp] = JDHfixedT_1cmp_CORR_fit(FJH, ExposureTime / 1000, D0, deltaZ/2);
%   [FJH_Coef2Cmp,FJH_Fit2Cmp, FJH_Sigma2Cmp] = JDHfixedT_2cmp_CORR_fit(FJH, ExposureTime / 1000, [D0 10*D0], deltaZ/2);
%   [FJH_Coef3Cmp,FJH_Fit3Cmp, FJH_Sigma3Cmp] = JDHfixedT_3cmp_CORR_fit(FJH, ExposureTime / 1000, [D0/10, D0, 10*D0], deltaZ/2);
% 
%   % Add fits of first histogram of displeacements to FJH.
%   FJH(:,3) = FJH_Fit1Cmp(:,2);
%   FJH(:,4) = FJH_Fit2Cmp(:,2);
%   FJH(:,5) = FJH_Fit3Cmp(:,2);
% 
%   rlist(1,2) =tlist(1);
% 
%   FitPar = [FJH_Coef1Cmp, FJH_Coef2Cmp, FJH_Coef3Cmp;...
%     FJH_Sigma1Cmp, 0, FJH_Sigma2Cmp, 0, FJH_Sigma3Cmp, 0];
% 
%   % Two component diffusion fit
%   FirstCMP = ...
%     JDHfixedT_1cmp_fun([FitPar(1,4)* FitPar(1,7), FitPar(1,5)],rlist);
%   SecondCMP = ...
%     JDHfixedT_1cmp_fun([FitPar(1,4)* (1 - FitPar(1,7)), FitPar(1,6)],rlist);
%   twoCMPFit = [FirstCMP, SecondCMP];
% 
%   % Three component diffusion fit
%   FirstCMP = ...
%     JDHfixedT_1cmp_fun([FitPar(1,9)* FitPar(1,13), FitPar(1,10)],rlist);
%   SecondCMP = ...
%     JDHfixedT_1cmp_fun([FitPar(1,9)* FitPar(1,14), FitPar(1,11)],rlist);
%   ThirdCMP = JDHfixedT_1cmp_fun...
%     ([FitPar(1,9)* (1 - FitPar(1,13) - FitPar(1,14)), FitPar(1,12)],rlist);
%   threeCMPFit = [FirstCMP, SecondCMP, ThirdCMP];
% 
%   save([output_path, Filenames{iter}, '_CMPFitPar.mat'], 'FJH');
%   save([output_path, Filenames{iter}, '_FitPar.mat'], 'FitPar');
%   save([output_path, Filenames{iter}, '_2CMPFit.mat'], 'twoCMPFit');
%   save([output_path, Filenames{iter}, '_3CMPFit.mat'], 'threeCMPFit');
% end
% sgtitle('Diffusion Coefficient for all population', 'interpreter', 'latex');

clear clip_factor analysis_type tracks rows_to_remove lfit D E msd ...
      subPlotNumbers tracked_files trackedPar traj_length track_length ...
      D0 tlist rlist JDH jdTracks binEdges ...
      FJH_Coef1Cmp FJH_Fit1Cmp FJH_Sigma1Cmp ...
      FJH_Coef2Cmp FJH_Fit2Cmp FJH_Sigma2Cmp ...
      FJH_Coef3Cmp FJH_Fit3Cmp FJH_Sigma3Cmp ...
      FitPar FirstCMP SecondCMP ThirdCMP twoCMPFit threeCMPFit

%% Functions
function msd = computeMSD(tracks, tol)
indices = 1: numel(tracks);
n_tracks = numel(indices);
all_delays = cell(n_tracks, 1);
for i = 1 : n_tracks
  index = indices(i);
  track = tracks(index).data;
  t = track(:,1);
  [T1, T2] = meshgrid(t, t);
  dT = round(abs(T1(:)-T2(:)), tol);
  all_delays{i} = unique(dT);
end
delays = unique( vertcat(all_delays{:}) );
n_delays = numel(delays);
msd = cell(n_tracks, 1);
for i = 1 : n_tracks
  mean_msd    = zeros(n_delays, 1);
  M2_msd2     = zeros(n_delays, 1);
  n_msd       = zeros(n_delays, 1);
  
  index = indices(i);
  track = tracks(index).data;
  t = track(:,1);
  t = round(t, tol);
  X = track(:, 2:end);
  
  n_detections = size(X, 1);
  
  for j = 1 : n_detections - 1
    
    % Delay in physical units
    dt = t(j+1:end) - t(j);
    dt = round(dt, tol);
    
    % Determine target delay index in bulk
    [~, index_in_all_delays, ~] = intersect(delays, dt);
    
    % Square displacement in bulk
    dX = X(j+1:end,:) - repmat(X(j,:), [(n_detections-j) 1] );
    dr2 = sum( dX .* dX, 2);
    
    % Store for mean computation / Knuth
    n_msd(index_in_all_delays)     = n_msd(index_in_all_delays) + 1;
    delta = dr2 - mean_msd(index_in_all_delays);
    mean_msd(index_in_all_delays) = mean_msd(index_in_all_delays) + delta ./ n_msd(index_in_all_delays);
    M2_msd2(index_in_all_delays)  = M2_msd2(index_in_all_delays) + delta .* (dr2 - mean_msd(index_in_all_delays));
  end
  
  n_msd(1) = n_detections;
  std_msd = sqrt( M2_msd2 ./ n_msd ) ;
  
  delay_not_present = n_msd == 0;
  mean_msd( delay_not_present ) = NaN;
  
  msd{index} = [ delays mean_msd std_msd n_msd ];
end
end

function lfit = fitMSD(msd, clip_factor, analysis_type)
if nargin < 2
  clip_factor = 0.25;
  analysis_type = "percentage";
end

n_spots = numel(msd);
if analysis_type == "percentage"
  if clip_factor < 1
    fprintf('Fitting %d curves of MSD = f(t), taking only the first %d%% of each curve... ',...
      n_spots, ceil(100 * clip_factor) )
  else
    fprintf('Fitting %d curves of MSD = f(t), taking only the first %d points of each curve... ',...
      n_spots, round(clip_factor) )
  end
end


a = NaN(n_spots, 1);
a_bounds = NaN(n_spots, 2);
b = NaN(n_spots, 1);
b_bounds = NaN(n_spots, 2);
r2fit = NaN(n_spots, 1);
ft = fittype('poly1');

fprintf('%4d/%4d', 0, n_spots);
for i_spot = 1 : n_spots
  
  msd_spot = msd{i_spot};
  
  t = msd_spot(:,1);
  y = msd_spot(:,2);
  w = msd_spot(:,4);
  
  if analysis_type == "percentage"
    % Clip data, never take the first one dt = 0
    if clip_factor < 1
      t_limit = 2 : round(numel(t) * clip_factor);
    else
      t_limit = 2 : min(1+round(clip_factor), numel(t));
    end
  elseif analysis_type == "number"
    t_limit = 2: clip_factor;
  end
  
  t = t(t_limit);
  y = y(t_limit);
  w = w(t_limit);
  
  % Thrash bad data
  nonnan = ~isnan(y);
  x = t(nonnan);
  y = y(nonnan);
  w = w(nonnan);
  
  if numel(y) < 2
    continue
  end
  
  [fo, gof] = fit(x, y, ft, 'Weights', w);
  
  if numel(x) > 3
    fo_bounds = confint(fo, 0.95);
    a_bounds(i_spot, :) = fo_bounds(1, :);
    b_bounds(i_spot, :) = fo_bounds(2, :);
  end
  
  a(i_spot) = fo.p1;
  b(i_spot) = fo.p2;
  r2fit(i_spot) = gof.adjrsquare;
  
end
lfit = struct(...
  'a', a, ...
  'a_bounds', a_bounds, ...
  'b', b, ...
  'b_bounds', b_bounds, ...
  'r2fit', r2fit);
end

function parsave(fname, trackedPar, settings)
  save(fname, 'trackedPar', 'settings')
end

function parsaveangle(fname, dataAngle, dataTraj, dataTrack, E, msd)
  save([fname, '_dataAngle.mat'], 'dataAngle');
  save([fname, '_dataTraj.mat'], 'dataTraj');
  save([fname, '_dataTrack.mat'], 'dataTrack');
  save([fname, '_Diffusion.mat'], 'E');
  save([fname, '_msd.mat'], 'msd');
end

function parsavedata(fname, FJH, FitPar, twoCMPFit, threeCMPFit)
  save([fname, '_CMPFitPar.mat'], 'FJH');
  save([fname, '_FitPar.mat'], 'FitPar');
  save([fname, '_2CMPFit.mat'], 'twoCMPFit');
  save([fname, '_3CMPFit.mat'], 'threeCMPFit');
end

function parsavecell(fname, cellData)
  save(fname, 'cellData');
end