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