%   Yew Yan Wong, October 2022
clear; clc;

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
%%%%%%%%%%%%%%%%%%%% DEFINE INPUT AND OUTPUT PATHS %%%%%%%%%%%%%%%%%%%%%%%%
% specify input path with tiff files:
input_path=('C:\Users\yeww\Desktop\New folder\');
output_path=('C:\Users\yeww\Desktop\New folder\Result\');
% add the neccesary paths:
addpath(genpath(['.' filesep 'Batch_MTT_code' filesep])); % MTT & BioFormats
disp('added paths for MTT algorithm mechanics, bioformats...');

zplanes = 45;
tplanes = 45;
analysis_type = "number"; % percentage or number for traj used
clip_factor = 4; % 0.8; % percentage or number of tracks in a trajectory trajectory to use for fitting of MSD
traj_length = 7; % Length of traj to keep (traj appear with less than this number of frame will be discarded)
min_traj = 1000; % Minimum trajectorys in a file to be accepted into the analysis
tol = 12; % Numbers of decimals to keep for rounding
bins = 20; % For plotting
LocalizationError = -6.5; % Localization Error: -6 = 10^-6
EmissionWavelength = 580; % wavelength in nm; consider emission max and filter cutoff
ExposureTime = 50; % in milliseconds
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
    data=buildTracks2_ASH(input_path, data,impars, locpars, trackpars, data.ctrsN, imgs_3d_double);
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
    
    ts = 0:zplanes:zplanes*tplanes;
    ts(end) = [];
    for n = 1 : zplanes
      dataLoc = find(data.frame == ts(1) + n);
      nodes = [data.ctrsX(dataLoc)*impars.PixelSize, data.ctrsY(dataLoc)*impars.PixelSize];
      scatter(nodes(:, 1), nodes(:, 2)); hold on;
      for m = 2 : tplanes
        dataLoc = find(data.frame == ts(m) + n);
        nodes2 = [data.ctrsX(dataLoc)*impars.PixelSize, data.ctrsY(dataLoc)*impars.PixelSize];
        scatter(nodes2(:, 1), nodes2(:, 2), 'r*');
        dist = pdist2(nodes, nodes2);
        % do X
        [nodesLoc, nodes2Loc] = find(dist <= 3);

        xs = data.ctrsX(dataLoc)*impars.PixelSize; ys = data.ctrsY(dataLoc)*impars.PixelSize;
        r = 0.05; th = 0:pi/50:2*pi;
        for i = 1 : length(data.ctrsX(dataLoc))
          x = xs(i); y = ys(i);
          xunit = r * cos(th) + x;
          yunit = r * sin(th) + y;
          h = plot(xunit, yunit);
        end

        % update nodes
        nodes = nodes2;
      end
    end

    %%%%%%%%% MTT ALGORITHM PART 2: TRACK PARTICLES BETWEEN FRAMES %%%%%%%%%
    disp('MTT ALGORITHM PART 2: track particles between frames');
    tic;
    disp(['tracking all localized particles from movie ', num2str(iter), ' of ', num2str(length(Filenames))]);
    data=buildTracks2_ASH(input_path, data,impars, locpars, trackpars, data.ctrsN, imgs_3d_double);
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