%   SerialProcess_PALM_JF549.m
%   Anders Sejr Hansen, August 2016
%   Yew Yan Wong, March 2022
clear; clc; %close all; clearvars -global

%   DESCRIPTION
%   This script takes as input a folder with tiff files and then outputs
%   workspaces with tracked single molecules. Briefly, it uses the
%   BioFormats package to read in nd2 files. Next, the script feeds the
%   images as a 3D matrix into the localization part of the MTT algorithm
%   (Part 1) and subsequently, the tracked particles are fed into the
%   tracking part of the MTT algorithm (Part 2). 

%   Version 220404:
%   Added ability to plot the line to divide bound and unbound state in
%   diffusion graph.
%   Version 220406:
%   Added the ability to run tif files reading and traj computing in
%   parallel.
%   Version 220407:
%   Added the ability to plot the line to divide the bound and unbound
%   state based on the peaks in the diffusion graph.
%   Version 220407b:
%   Added the ability to plot different error bars (standard deviation and
%   standard error of mean).
%   Version 220408:
%   Added the ability to plot mean square displacement graphs.
%   Version 220408b:
%   Added the ability to filter out cells that have less than a certain
%   number of trajectory recorded (quality control purpose).
%   Version 220411:
%   Select only first 10 time frame data to plot mean square displacement
%   graph and clearing unused variables at end of each stage.
%   Version 220411b:
%   Gathered all the msd into msd_all so as to be able to compute the
%   standard deviation of msd. 
%%%%%%%%%%%%%%%%%%%% DEFINE INPUT AND OUTPUT PATHS %%%%%%%%%%%%%%%%%%%%%%%%
% specify input path with tiff files:
% input_path=('C:\Users\yeww\Desktop\Data\MTTTest\');
% input_path = 'D:\Data\Susav\Nuc-red_sox18_Susav-Yew-Analysis\Nucred-649nm_sox18-halo-549nm\Test\';
input_path = 'D:\Data\MTTTest\'; %D:\Data\Random Test Data\';
output_path= 'D:\Data\MTTTest\'; %('C:\Users\yeww\Desktop\Data\MTTTest\');
% add the neccesary paths:
addpath(genpath(['.' filesep 'Batch_MTT_code' filesep])); % MTT & BioFormats
disp('added paths for MTT algorithm mechanics, bioformats...');


analysis_type = "number"; % percentage or number for traj used
clip_factor = 4; % 0.8; % percentage or number of tracks in a trajectory trajectory to use for fitting of MSD
traj_length = 7; % Length of traj to keep (traj appear with less than this number of frame will be discarded)
min_traj = 1000; % Minimum trajectorys in a file to be accepted into the analysis
tol = 12; % Numbers of decimals to keep for rounding
bins = 20; % For plotting
LocalizationError = -6.5; % Localization Error: -6 = 10^-6
EmissionWavelength = 580; % wavelength in nm; consider emission max and filter cutoff
ExposureTime = 20; % in milliseconds
NumDeflationLoops = 0; % Generaly keep this to 0; if you need deflation loops, you are imaging at too high a density;
MaxExpectedD = 2; % The maximal expected diffusion constant for tracking in units of um^2/s;
NumGapsAllowed = 1; % the number of gaps allowed in trajectories

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
runParallel = false; % to make use of multi-cores architecture
numCores = 16; % define number of cores (not thread) to use

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%% DEFINE STRUCTURED ARRAY WITH ALL THE SPECIFIC SETTINGS FOR LOC AND TRACK
% imaging parameters
impars.PixelSize=0.13; % um per pixel
impars.psf_scale=1.35; % PSF scaling
impars.wvlnth= EmissionWavelength/1000; %emission wavelength in um
impars.NA=1.49; % NA of detection objective
impars.psfStd= impars.psf_scale*0.55*(impars.wvlnth)/impars.NA/1.17/impars.PixelSize/2; % PSF standard deviation in pixels
impars.FrameRate= ExposureTime/1000; %secs
impars.FrameSize= ExposureTime/1000; %secs

% localization parameters
locpars.wn=9; %detection box in pixels
locpars.errorRate= LocalizationError; % error rate (10^-)
locpars.dfltnLoops= NumDeflationLoops; % number of deflation loops
locpars.minInt=0; %minimum intensity in counts
locpars.maxOptimIter= 50; % max number of iterations
locpars.termTol= -2; % termination tolerance
locpars.isRadiusTol=false; % use radius tolerance
locpars.radiusTol=50; % radius tolerance in percent
locpars.posTol= 1.5;%max position refinement
locpars.optim = [locpars.maxOptimIter,locpars.termTol,locpars.isRadiusTol,locpars.radiusTol,locpars.posTol];
locpars.isThreshLocPrec = false;
locpars.minLoc = 0;
locpars.maxLoc = inf;
locpars.isThreshSNR = false;
locpars.minSNR = 0;
locpars.maxSNR = inf;
locpars.isThreshDensity = false;

% tracking parameters
trackpars.trackStart=1;
trackpars.trackEnd=inf;
trackpars.Dmax= MaxExpectedD;
trackpars.searchExpFac=1.2;
trackpars.statWin=10;
trackpars.maxComp=3; %TODO
trackpars.maxOffTime=NumGapsAllowed;
trackpars.intLawWeight=0.9;
trackpars.diffLawWeight=0.5;

%%
% add the required functions to the path:
% clear EmissionWavelength LocalizationError NumDeflationLoops MaxExpectedD NumGapsAllowed
% disp('added paths for MTT algorithm mechanics, bioformats...');

%%%%%%%%%%%%%% READ IN TIF FILES %%%%%%%%%%%%%%%%
%disp('-----------------------------------------------------------------');
%disp('reading in tif files; writing out MAT workspaces...');
%find all tif files:
tif_files=dir([input_path,'*.tif']);
Filenames = ''; 
for iter = 1:length(tif_files)
    Filenames{iter} = tif_files(iter).name(1:end-4);
end
tWhole = tic;
if runParallel
  temp_struct_for_save = struct;
  % Check if the user's machine has the number of cores they desired to use
  if numCores > feature('numcores')
    %   reduce the cores to use to the machine's maximum number of cores
    numCores = feature('numcores');
  end
  % if there's less files to run than number of cores, reduce the core to use even further
  parpool('local', min([numCores, length(Filenames)]));
  parfor iter = 1:length(Filenames)
    disp('-----------------------------------------------------------------');
    tic;
    disp(['reading in TIFF file ', num2str(iter), ' of ', num2str(length(tif_files)), ' total TIFF files']);
    %%% read tiff files:
    [stack, nbImages] = tiffread([input_path, Filenames{iter}, '.tif']);
    
    % convert to 3D matrix as double:
    imgs_3d_double = zeros(size(stack(1,1).data,1), size(stack(1,1).data,2), nbImages);
    for img_iter = 1:nbImages
      imgs_3d_double(:,:,img_iter) = stack(img_iter).data;
    end
    
    toc;
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    
    %%%%%%%%%%%% MTT ALGORITHM PART 1: LOCALIZE ALL PARTICLES %%%%%%%%%%%%%%
    disp('MTT ALGORITHM PART 1: localize particles in all of the workspaces');
    tic;
    disp(['localizing all particles in movie number ', num2str(iter), ' of ', num2str(length(Filenames))]);
%     impars.name = Filenames{iter};
    data = localizeParticles_ASH(input_path,impars, locpars, imgs_3d_double);
    toc;
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    
    %%%%%%%%% MTT ALGORITHM PART 2: TRACK PARTICLES BETWEEN FRAMES %%%%%%%%%
    disp('MTT ALGORITHM PART 2: track particles between frames');
    tic;
    disp(['tracking all localized particles from movie ', num2str(iter), ' of ', num2str(length(Filenames))]);
    data=buildTracks2_ASH(output_path, Filenames{iter}, data, impars, locpars, trackpars, data.ctrsN, imgs_3d_double);
    toc;
    
    temp_struct_for_save(iter).data_cell_array = data.tr;
    temp_struct_for_save(iter).Width = size(imgs_3d_double,2);
    temp_struct_for_save(iter).Height = size(imgs_3d_double,1);
    temp_struct_for_save(iter).Frames = size(imgs_3d_double,3);
  end
else % single core
  for iter = 1:length(Filenames)
    disp('-----------------------------------------------------------------');
    tic;
    disp(['reading in TIFF file ', num2str(iter), ' of ', num2str(length(tif_files)), ' total TIFF files']);
    %%% read tiff files:
    [stack, nbImages] = tiffread([input_path, Filenames{iter}, '.tif']);
    
    % convert to 3D matrix as double:
    imgs_3d_double = zeros(size(stack(1,1).data,1), size(stack(1,1).data,2), nbImages);
    for img_iter = 1:nbImages
      imgs_3d_double(:,:,img_iter) = stack(img_iter).data;
    end
    
    toc;
    clear stack
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    
    %%%%%%%%%%%% MTT ALGORITHM PART 1: LOCALIZE ALL PARTICLES %%%%%%%%%%%%%%
    disp('MTT ALGORITHM PART 1: localize particles in all of the workspaces');
    tic;
    disp(['localizing all particles in movie number ', num2str(iter), ' of ', num2str(length(Filenames))]);
    impars.name = Filenames{iter};
    data = localizeParticles_ASH(input_path,impars, locpars, imgs_3d_double);
    toc;
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    
    %%%%%%%%% MTT ALGORITHM PART 2: TRACK PARTICLES BETWEEN FRAMES %%%%%%%%%
    disp('MTT ALGORITHM PART 2: track particles between frames');
    tic;
    disp(['tracking all localized particles from movie ', num2str(iter), ' of ', num2str(length(Filenames))]);
    data=buildTracks2_ASH(output_path, Filenames{iter}, data, impars, locpars, trackpars, data.ctrsN, imgs_3d_double);
    toc;
    
    %%%%%%%% SAVE THE TRAJECTORIES TO YOUR STRUCTURED ARRAY FORMAT %%%%%%%%
    tic;
    disp(['saving MATLAB workspace for movie ', num2str(iter), ' of ', num2str(length(Filenames))]);
    data_cell_array = data.tr;
    if length(data_cell_array) < min_traj
      continue
    end
    % save meta-data
    settings.Delay = impars.FrameRate;
    settings.px2micron = impars.PixelSize;
    settings.TrackingOptions = trackpars;
    settings.LocOptions = locpars;
    settings.AcquisitionOptions = impars;
    settings.Filename = impars.name;
    settings.Width = size(imgs_3d_double,2);
    settings.Height = size(imgs_3d_double,1);
    settings.Frames = size(imgs_3d_double,3);
    trackedPar = struct;
    for i=1:length(data_cell_array)
      %convert to um:
      trackedPar(1,i).xy =  impars.PixelSize .* data_cell_array{i}(:,1:2);
      trackedPar(i).Frame = data_cell_array{i}(:,3);
      trackedPar(i).TimeStamp = impars.FrameRate.* data_cell_array{i}(:,3);
    end
    disp(['Localized and tracked ', num2str(length(trackedPar)), ' trajectories']);
    save([output_path, Filenames{iter}, '_Tracked.mat'], 'trackedPar', 'settings');
    toc;
    % Producing data for dashboard
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

    trackedData = ["TF_number" "Frame" "x_coord" "y_coord"];
    for n = 1 : length(tracks)
      track_length = size(tracks(n).data, 1);
      trackedData = [trackedData; [repelem(1, track_length)' tracks(n).data(:, 1)./impars.FrameRate tracks(n).data(:, 2:3)]];
    end
    writematrix(trackedData, strcat(output_path, "fast_", extractBefore(Filenames(iter),".tif")), 'Delimiter', ',')
    clear imgs_3d_matrix imgs_3d_double data_cell_array trackedPar
    disp('-----------------------------------------------------------------');
  end
end

% Compiling data if ran with multi-core
if runParallel
  p = gcp;
  delete(p)
  for iter = 1:length(Filenames)
    %%%%%%%% SAVE THE TRAJECTORIES TO YOUR STRUCTURED ARRAY FORMAT %%%%%%%%
    tic;
    disp(['saving MATLAB workspace for movie ', num2str(iter), ' of ', num2str(length(Filenames))]);
    data_cell_array = temp_struct_for_save(iter).data_cell_array;
    if length(data_cell_array) < min_traj
      continue
    end
    % save the name:
    impars.name = Filenames{iter};
    % save meta-data
    settings.Delay = impars.FrameRate;
    settings.px2micron = impars.PixelSize;
    settings.TrackingOptions = trackpars;
    settings.LocOptions = locpars;
    settings.AcquisitionOptions = impars;
    settings.Filename = impars.name;
    settings.Width = temp_struct_for_save(iter).Width;
    settings.Height = temp_struct_for_save(iter).Height;
    settings.Frames = temp_struct_for_save(iter).Frames;
    trackedPar = struct;
    for i=1:length(data_cell_array)
      %convert to um:
      trackedPar(1,i).xy =  impars.PixelSize .* data_cell_array{i}(:,1:2);
      trackedPar(i).Frame = data_cell_array{i}(:,3);
      trackedPar(i).TimeStamp = impars.FrameRate.* data_cell_array{i}(:,3);
    end
    disp(['Localized and tracked ', num2str(length(trackedPar)), ' trajectories']);
    save([output_path, Filenames{iter}, '_Tracked.mat'], 'trackedPar', 'settings');
    toc;
    % Producing data for dashboard
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

    trackedData = ["TF_number" "Frame" "x_coord" "y_coord"];
    for n = 1 : length(tracks)
      track_length = size(tracks(n).data, 1);
      trackedData = [trackedData; [repelem(n, track_length)' tracks(n).data(:, 1)./impars.FrameRate tracks(n).data(:, 2:3)]];
    end
    writematrix(trackedData, strcat(output_path, "fast_", extractBefore(Filenames(iter),".tif")), 'Delimiter', ',')
    clear imgs_3d_matrix imgs_3d_double data_cell_array trackedPar
    disp('-----------------------------------------------------------------');
  end
end
tEnd = toc(tWhole)
clear input_path Boule_free tWhole tEnd sig_free T T_off tif_files ...
      runParallel numCores i im_t img_iter Nb_combi Nb_STK nbImages ...
      settings impars iter locpars trackpars Poids_melange_aplha ...
      Poids_melange_diff data Filenames nblmages t_red min_traj ...
      tracks rows_to_remove trackedData track_length

%% Producing diffusion data
tracked_files=dir([output_path,'*_Tracked.mat']);
Filenames = ''; %for saving the actual file name
subPlotNumbers = ceil(sqrt(length(tracked_files)));

figure;
for iter = 1:length(tracked_files)
  Filenames{iter} = tracked_files(iter).name(1:end-4);
  load([output_path, Filenames{iter}, '.mat']);
  
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

  %
  trackedPar(rows_to_remove) = [];
  negativeTrackedPar = trackedPar(lfit.a<=0);
  trackedPar = trackedPar(lfit.a>0);
  %
  
  subplot(subPlotNumbers, subPlotNumbers, iter);
  hist(log10(lfit.a(lfit.a>0)), 15); hold on;
  histogram(log10(lfit.a(lfit.a>0)), 15, 'FaceAlpha', 0.5, 'EdgeAlpha', 0.5);
  legend(["Old method", "New method"])
  title(Filenames{iter}, 'interpreter', 'none');
  xlabel('Log10(D(um2/s)', 'interpreter', 'latex');
  ylabel('Counts', 'interpreter', 'latex');
  
  D = log10(lfit.a(lfit.a>0));
  E = lfit.a(lfit.a>0);
  
  save([output_path, Filenames{iter}, '_Negative_Track.mat'], 'negativeTrackedPar');
  save([output_path, Filenames{iter}, '_Log_Diffusion.mat'], 'D');
  save([output_path, Filenames{iter}, '_tracks_filtered.mat'], 'trackedPar');
  save([output_path, Filenames{iter}, '_Diffusion.mat'], 'E');
  save([output_path, Filenames{iter}, '_msd.mat'], 'msd');
end
sgtitle('Diffusion Coefficient for all population', 'interpreter', 'latex');

% clear clip_factor analysis_type tracks rows_to_remove lfit D E msd ...
%       subPlotNumbers tracked_files trackedPar traj_length track_length

%% Plotting diffusion graphs
diffusion_files = dir([output_path,'*_Diffusion.mat']);
cell_types = "";

number_of_cells = numel(diffusion_files);
for iter = 1:numel(diffusion_files)
    cell_types{iter} = extractBefore(diffusion_files(iter).name,"_");
end
cell_types = unique(cell_types);

xbins = linspace(-4,2, bins);
% figure;
y_all = zeros(number_of_cells, size(xbins, 2), size(cell_types, 2));
y_all_o = zeros(number_of_cells, size(xbins, 2), size(cell_types, 2));
cell_types_number = zeros(size(cell_types, 2) + 1, 1);
for n = 1:number_of_cells
  load([output_path, diffusion_files(n).name]);
  cell_type = find(cell_types == extractBefore(diffusion_files(n).name,"_"));
  
  % old method
  [fo,xo] = hist(log10(E),xbins);
  yo = fo/trapz(xo,fo);
  y_all_o(n, :, cell_type) = yo;

  % correct method
  f = histcounts(log10(E), xbins);
  y = f/trapz(xbins, [0 f]);
%   plot(x, y, '-+k', 'linewidth', 2); hold on;
  y_all(n, 2:end, cell_type) = y;
  cell_types_number(cell_type + 1) = cell_types_number(cell_type + 1) + 1;
end

ylimit = round(max(max(max(y_all, [], 2), [], 1), [], 3), 2);
figure;
current_count = 0;
for n = 1:size(cell_types, 2)
  y_all_cell_type = y_all(current_count + 1:current_count + cell_types_number(n + 1), :, n);
  y_all_cell_type_o = y_all_o(current_count + 1:current_count + cell_types_number(n + 1), :, n);
  avg_y = mean(y_all_cell_type, 1);
  avg_y_o = mean(y_all_cell_type_o, 1);
  current_count = current_count + cell_types_number(n + 1);
  errorbar(xbins, avg_y_o, avg_y_o - min(y_all_cell_type_o, [], 1), max(y_all_cell_type_o, [], 1) - avg_y_o, 'b-+'); hold on;
  errorbar(xbins, avg_y, avg_y - min(y_all_cell_type, [], 1), max(y_all_cell_type, [], 1) - avg_y, 'r-+');
end
title('Diffusion Coefficient Density with Different Approach', 'interpreter', 'latex');
xlabel('Log10($D(um^2/s)$)', 'interpreter', 'latex');
ylabel('Density', 'interpreter', 'latex');
legend(["Old Method", "New Method"], 'interpreter', 'latex');
xlim([-4, 2]);
ylim([0, ylimit]);

figure;
current_count = 0; diffusion_threshold_line = zeros(size(cell_types, 2), 4);
for n = 1:size(cell_types, 2)
  y_all_cell_type = y_all(current_count + 1:current_count + cell_types_number(n + 1), :, n);
  avg_y = mean(y_all_cell_type, 1);
  current_count = current_count + cell_types_number(n + 1);
  p = errorbar(xbins, avg_y, avg_y - min(y_all_cell_type, [], 1), max(y_all_cell_type, [], 1) - avg_y, '-+'); hold on;
%   peaks = findpeaks(avg_y);
  % if more than 2 peaks, pick 2 biggest peaks
%   if length(peaks) > 2
%     peaks_sorted = sort(peaks);
%     peaks = peaks_sorted(end-1 : end);
%   end
%   xFirstPeak = xbins(avg_y == peaks(1)); xSecondPeak = xbins(avg_y == peaks(2));
%   xMiddlePeak = (xFirstPeak(end) + xSecondPeak(end)) / 2;
%   diffusion_threshold_line(n, :) = [xMiddlePeak p.Color];
end
% for n = 1:size(cell_types, 2)
%   diffusion_threshold = diffusion_threshold_line(n, 1);
%   plot([diffusion_threshold diffusion_threshold], ylim, '--', 'color', diffusion_threshold_line(n, 2:4));
% end
title('Data Variation Error Bar', 'interpreter', 'latex');
xlabel('Log10($D(um^2/s)$)', 'interpreter', 'latex');
ylabel('Density', 'interpreter', 'latex');
legend(cell_types, 'interpreter', 'latex');
xlim([-4, 2]);
ylim([0, ylimit]);

figure;
current_count = 0; diffusion_threshold_line = zeros(size(cell_types, 2), 4);
for n = 1:size(cell_types, 2)
  y_all_cell_type = y_all(current_count + 1:current_count + cell_types_number(n + 1), :, n);
  avg_y = mean(y_all_cell_type, 1);
  current_count = current_count + cell_types_number(n + 1);
  p = errorbar(xbins, avg_y, std(y_all_cell_type, 0, 1)/2, std(y_all_cell_type, 0, 1)/2, '-+'); hold on;
%   peaks = findpeaks(avg_y);
  % if more than 2 peaks, pick 2 biggest peaks
%   if length(peaks) > 2
%     peaks_sorted = sort(peaks);
%     peaks = peaks_sorted(end-1 : end);
%   end
%   xFirstPeak = xbins(avg_y == peaks(1)); xSecondPeak = xbins(avg_y == peaks(2));
%   xMiddlePeak = (xFirstPeak(end) + xSecondPeak(end)) / 2;
%   diffusion_threshold_line(n, :) = [xMiddlePeak p.Color];
end
% for n = 1:size(cell_types, 2)
%   diffusion_threshold = diffusion_threshold_line(n, 1);
%   plot([diffusion_threshold diffusion_threshold], ylim, '--', 'color', diffusion_threshold_line(n, 2:4));
% end
title('Standard Deviation Error Bar', 'interpreter', 'latex');
xlabel('Log10($D(um^2/s)$)', 'interpreter', 'latex');
ylabel('Density', 'interpreter', 'latex');
legend(cell_types, 'interpreter', 'latex');
xlim([-4, 2]);
ylim([0, ylimit]);

figure;
current_count = 0; diffusion_threshold_line = zeros(size(cell_types, 2), 4);
for n = 1:size(cell_types, 2)
  y_all_cell_type = y_all(current_count + 1:current_count + cell_types_number(n + 1), :, n);
  avg_y = mean(y_all_cell_type, 1);
  current_count = current_count + cell_types_number(n + 1);
  p = errorbar(xbins, avg_y, std(y_all_cell_type, 0, 1)/(2 * sqrt(cell_types_number(n + 1))), std(y_all_cell_type, 0, 1)/(2 * sqrt(cell_types_number(n + 1))), '-+'); hold on;
%   peaks = findpeaks(avg_y);
  % if more than 2 peaks, pick 2 biggest peaks
%   if length(peaks) > 2
%     peaks_sorted = sort(peaks);
%     peaks = peaks_sorted(end-1 : end);
%   end
%   xFirstPeak = xbins(avg_y == peaks(1)); xSecondPeak = xbins(avg_y == peaks(2));
%   xMiddlePeak = (xFirstPeak(end) + xSecondPeak(end)) / 2;
%   diffusion_threshold_line(n, :) = [xMiddlePeak p.Color];
end
% for n = 1:size(cell_types, 2)
%   diffusion_threshold = diffusion_threshold_line(n, 1);
%   plot([diffusion_threshold diffusion_threshold], ylim, '--', 'color', diffusion_threshold_line(n, 2:4));
% end
title('Standard Error of Mean Error Bar', 'interpreter', 'latex');
xlabel('Log10($D(um^2/s)$)', 'interpreter', 'latex');
ylabel('Density', 'interpreter', 'latex');
legend(cell_types, 'interpreter', 'latex');
xlim([-4, 2]);
ylim([0, ylimit]);

clear avg_y bins current_count diffusion_files diffusion_threshold...
      diffusion_threshold_line E f Filenames iter n p peaks peaks_sorted ...
      tol x xbins y y_all y_all_cell_type ylimit

%% Plotting msd graphs
msd_files = dir([output_path,'*_msd.mat']);
number_of_cells = numel(msd_files);

max_time = 0; total_traj = 0;
for n = 1 : number_of_cells
  load([output_path, msd_files(n).name]);
  if size(msd{1}, 1) > max_time
    max_time = size(msd{1}, 1);
  end
  total_traj = total_traj + size(msd, 1);
end
msd_all = zeros(total_traj, max_time);

cell_types_number = zeros(size(cell_types, 2) + 1, 1);
cell_types_traj_count = zeros(size(cell_types, 2) + 1, 1);
current_line = 1;
for n = 1 : number_of_cells
  load([output_path, msd_files(n).name]);
  cell_type = find(cell_types == extractBefore(msd_files(n).name,"_"));
  for m = 1 : size(msd, 1)
    msd_all(current_line, :) = [msd{m}(:, 2)' nan(1, max_time - length(msd{m}(:, 2)'))];
    current_line = current_line + 1;
  end
  cell_types_number(cell_type + 1) = cell_types_number(cell_type + 1) + 1;
  cell_types_traj_count(cell_type + 1) = cell_types_traj_count(cell_type + 1) + size(msd, 1);
end

figure;
current_line = 1;
time_plot = 0 : ExposureTime / 1000 : (ExposureTime / 1000) * (max_time - 1);
for n = 1:size(cell_types, 2)
  mean_msd_plot = mean(msd_all(current_line : current_line + cell_types_traj_count(n + 1) - 1, :), 1, "omitnan");
  std_msd_plot = std(msd_all(current_line : current_line + cell_types_traj_count(n + 1) - 1, :), 1, "omitnan");
  current_line = current_line + cell_types_traj_count(n + 1);
%   plot(time_plot(1:10), mean_msd_plot(1:10)); hold on;
  errorbar(time_plot(1:10), mean_msd_plot(1:10), std_msd_plot(1:10)./2, std_msd_plot(1:10)./2, '-+'); hold on;
end
title('Average Mean Square Displacement', 'interpreter', 'latex');
xlabel('Time $(s)$', 'interpreter', 'latex');
ylabel('Mean Square Displacement $(\mu m ^ 2)$', 'interpreter', 'latex');
legend(cell_types, 'interpreter', 'latex');

clear cell_type cell_types cell_types_number ExposureTime m max_time ...
      mean_msd_plot msd msd_all msd_files n number_of_cells output_path ...
      temp_msd time_plot total_traj current_line cell_types_traj_count

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
%   [fo, gof] = fit(x, y, 'poly1', 'Weights', w, 'Lower', [0,0]);
  
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