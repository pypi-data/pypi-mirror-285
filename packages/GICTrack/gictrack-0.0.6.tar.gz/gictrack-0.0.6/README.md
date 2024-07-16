# GIC-Track
This dashboard is designed for the spatial and temporal analysis of fluorescently tagged transcription factors within cell nuclei.

# Requirement
This dashboard requires MATLAB with Statistics and Curve Fitting toolbox installed.

# Dashboard Usage
1. More than one file (.tif for pre-processed files, .mat for post-processed files) could be uploaded at the same time from the "Upload" tab using the respective buttons.
2. The files could be in any directory; however, they follow a specific naming convention. The dashboard would classify the files uploaded based on the naming convention; with the string/text before the first "_" being used as condition type to group the file/cell data.
Below are some example of the file name convention for comparing between 2 conditions of 3 files each: <br>
Condition-1_Cell_1.tiff <br>
Condition-1_Cell_2.tiff <br>
Condition-1_Cell_3.tiff <br>
Condition-2_Cell_1.tiff <br>
Condition-2_Cell_2.tiff <br>
Condition-2_Cell_3.tiff <br>
3. If you have a background image that you want to use as overlay and/or comparison (DAPI or Hoist stain compare to trajectories, you can upload the DAPI/Hoechst file together with previous step, naming the file as WT_Cell1_DAPI.tif (even if it's Hoechst stain, currently it looks for "_DAPI" to existing file name and mark it as a background file).
4. After pressing the "Upload" button and selecting the files. The dashboard will process all the data on its own (it may show a MATLAB info tab on the progress, I have not tested if this will happen on a Mac/Linux system). Once it's done processing all the files, you should be able to go to any tabs in any order and you can view the visualisation of the data it processed.

## A few known issues that are being worked on and workaround are as follows:
1. If the dashboard crashes when visiting certain tabs, it could be that some file has mistakenly got recorded onto the dashboard.db despite it failing the Quality Control (QC) that was marked on the Upload tab. Thsis result in the dashboard crashes when attempting to view these data.
Workaround: Delete the database.db and re-upload new data with lower QC requirement (the "Clip Factor", "Trajectory Length" and "Minimum Number of Trajectory" undering the "Generic Parameters" are the most important parameters. Try changing the "Analysis Type" to "Percentage", "Clip Factor" to 100, "Trajectory Length" to 1 and "Minimum Number of Trajectory" to 1 to accept all data.
2. "Angle Plots" tab can crash when data with too short duration or translocation distance exist in the database.


# Data Table Format
## FileList
| Parameter | Type | Description |
| --- | --- | --- |
| filename | TEXT | The filename that contribute to the dataset. |
| mutation | TEXT | The condition of the file/cell data, created based on file naming convention. |
| acquisition_rate | TEXT | "fast" or "slow", used to differentiate the data acquisition rate to prevent mixing of data types. |
| exposure_time | REAL| Exposure time in ms. |
| pixelSize | REAL | Pixel size of the data (in &mu;m). |
| cellSize | REAL | The size of the cell/nucleus based on segmented data (in pixels). |
| psfScale | REAL | Point spread function value of the microscope (user input in dashboard). |
| wvlngth | REAL | The wavelength of the emission used by the microscope (user input in dashboard). |
| iNA | REAL | The "Numerical Aperture" of the microscope used to gather the data (user input in dashboard).|
| psfStd | REAL | The deviation of the "point spread function" based on "psfScale", "wvlnth", "iNA" and "pixelSize". $psfStd = \frac{psf\textunderscore scale * \left( 0.55 * wvlnth \right)}{2 * iNA * pixelSize * 1.17}$ |
| wn | REAL | Spatial sliding window width used for particle detection (in pixels). |
| errorRate | REAL | The maximum difference between $H_{0}$ and $H_{1}$ hypothesis that are still accepted as a detected point. <br> Refer to [Sergé et al. Nature Methods 5:687-694 (2008)](https://www.nature.com/articles/nmeth.1233)'s [Supplementary Text and Figures](https://static-content.springer.com/esm/art%3A10.1038%2Fnmeth.1233/MediaObjects/41592_2008_BFnmeth1233_MOESM292_ESM.pdf)'s Equation [4].|
| dfltnLoops | REAL | Number of deflation loops (usually 0, but useful if the image density is too high).  |
| minInt | REAL | Minimum intensity to be classified as a point. |
| optim_MaxIter | REAL | The maximum number of iteration allowed during localization optimization. |
| optim_termTol | REAL | The termination tolerance (the value is 10 to the power of the input value). If the variation of x and y coordinates is lesser than this, the iteration will stop (variation of Gaussian radius will be checked as well if "optim_isRadTol" is activated). |
| optim_isRadTol | INTEGER | Is Gaussian radius variation tolerance feature used for the localization algorithm (user input in dashboard). |
| optim_radiusTol | REAL | The Gaussian radius tolerance (in percentage) with respect to "point spread function deviation" (psfStd). |
| optim_posTol | REAL | The tolerance for the x and y coordinates of the point detected during the localization (in pixels). |
| isThreshLocPrec | INTEGER |  **Currently not being used.** <br> Is radius tolerance feature used for the tracking algorithm (user input in dashboard). |
| minLoc | REAL | **Currently not being used.** |
| maxLoc | REAL | **Currently not being used.** |
| isThreshSNR | INTEGER |  **Currently not being used.** <br> Is signal-to-noise threshold feature used for the tracking algorithm (user input in dashboard). |
| minSNR | REAL | **Currently not being used.** |
| maxSNR | REAL | **Currently not being used.** |
| isThreshDensity | INTEGER |  **Currently not being used.** <br> Is density threshold feature used for the tracking algorithm (user input in dashboard). |
| trackStart | REAL | **Currently not being used.** |
| trackEnd | REAL | **Currently not being used.** |
| Dmax | REAL | The maximum expected diffusion coefficient (in &mu;m<sup>2</sup>/s) of the uploaded file (user input in dashboard). |
| searchExpFac | REAL | Search exploration factor. <br> The maximum amount a trajectory can move is computed as $searchExpFac * \frac{Dmax}{pixelSize^{2} * 4 * \frac{exposureTime}{1000}}$. |
| statWin | REAL | Number of frames data to be used in computing trajectories data. |
| maxComp | REAL | Maximum number of trajectories a point can belong to (during trajectories forming stage). |
| maxOffTime | REAL | Maximum number of frames allowed to be in-between a trajectory for it to still be classify as the same trajectory (for situation where particles could fade out of focus). |
| intLawWeight | REAL | The intensity probability law weighting, value ranges from 0 to 1.0, with 1.0 accounting for intensity staying on and 0 accounting for blinking state. <br> The reconnection procedure take into account the point's intensity, diffusion and blinking. |
| diffLawWeight | REAL | The diffusion probability law weighting, value ranges from 0 to 1.0, with 1.0 accounting for local diffusion (based on estimated standard deviation of diffusion based on "statWin" number of past frames information) and 0 accounting for free diffusion. <br> The reconnection procedure take into account the point's intensity, diffusion and blinking, a value of 0.9 with emphasizes on local behaviour while allowing the possibility of a sudden increase towards free diffusion. |
| bleach_rate | REAL | The initial value used to estimate long dwell time activity. Long dwell time is computed as follows: <br> $t = \frac{\left( bleach\textunderscore rate - 1 \right)}{\frac{bleach\textunderscore rate}{max\left( \tau_{s}, \tau_{ns} \right) - 1}}$ where $\tau_{s}$ is the long dwell time from the fitting model and $\tau_{ns}$ is short dwell time from the fitting model. |
| traj_length | INTEGER | **Quality Control:** The minimum number of tracks in a trajectory (trajectories with fewer number than this will be discarded). |
| min_traj | INTEGER | **Quality Control:** The minimum number of trajectories in a file (files with fewer trajectories than this number will be discarded). |
| clip_factor | INTEGER | The number/percentage (depending on "Analysis Type:" selected in the dashboard) of a trajectories (from when it first being formed) to be used in the "mean square displacement" analysis.|
| tol | INTEGER | The number of decimals to keep during during computation of "mean square displacement". |
| twoParN | REAL | The number of tracks that are used in two parameters fitting (used for jump distance plots in the dashboard). |
| twoPardN | REAL | The number of tracks variation that are used in two parameters fitting (used for jump distance plots in the dashboard). |
| twoParD1 | REAL | The "immobile" diffusion coefficient (in &mu;m<sup>2</sup>/s) computed from two parameters fitting model (used for jump distance plots in the dashboard). |
| twoPardD1 | REAL | The variation of "immobile" diffusion coefficient (in &mu;m<sup>2</sup>/s) computed from two parameters fitting model (used for jump distance plots in the dashboard). |
| twoParD2 | REAL | The variation of "mobile" diffusion coefficient (in &mu;m<sup>2</sup>/s) computed from two parameters fitting model (used for jump distance plots in the dashboard). |
| twoPardD2 | REAL | The variation of "mobile" diffusion coefficient (in &mu;m<sup>2</sup>/s) computed from two parameters fitting model (used for jump distance plots in the dashboard). |
| twoParf1 | REAL | The fraction of "immobile" tracks computed from two parameters fitting model (used for jump distance plots in the dashboard). |
| twoPardf1 | REAL | The variation of fraction of "immobile" tracks computed from two parameters fitting model (used for jump distance plots in the dashboard). |
| twoParSSR | REAL | The "sum of squares due to regression" of the two parameters fitting model (used for jump distance plots in the dashboard).  |
| threeParN | REAL | The number of tracks that are used in three parameters fitting (used for jump distance plots in the dashboard). |
| threePardN | REAL | The number of tracks variation that are used in three parameters fitting (used for jump distance plots in the dashboard). |
| threeParD1 | REAL | The "immobile" diffusion coefficient (in &mu;m<sup>2</sup>/s) computed from three parameters fitting model (used for jump distance plots in the dashboard). |
| threePardD1 | REAL | The variation of "immobile" diffusion coefficient (in &mu;m<sup>2</sup>/s) computed from three parameters fitting model (used for jump distance plots in the dashboard). |
| threeParD2 | REAL | The variation of "mixed" diffusion coefficient (in &mu;m<sup>2</sup>/s) computed from three parameters fitting model (used for jump distance plots in the dashboard). |
| threePardD2 | REAL | The variation of "mixed" diffusion coefficient (in &mu;m<sup>2</sup>/s) computed from three parameters fitting model (used for jump distance plots in the dashboard). |
| threeParD3 | REAL | The variation of "mobile" diffusion coefficient (in &mu;m<sup>2</sup>/s) computed from three parameters fitting model (used for jump distance plots in the dashboard). |
| threePardD3 | REAL | The variation of "mobile" diffusion coefficient (in &mu;m<sup>2</sup>/s) computed from three parameters fitting model (used for jump distance plots in the dashboard). |
| threeParf1 | REAL | The fraction of "immobile" tracks computed from three parameters fitting model (used for jump distance plots in the dashboard). |
| threePardf1 | REAL | The variation of fraction of "immobile" tracks computed from three parameters fitting model (used for jump distance plots in the dashboard). |
| threeParf2 | REAL | The fraction of "mixed" tracks computed from three parameters fitting model (used for jump distance plots in the dashboard). |
| threePardf2 | REAL | The variation of fraction of "mixed" tracks computed from three parameters fitting model (used for jump distance plots in the dashboard). |
| threeParSSR | REAL | The "sum of squares due to regression" of the three parameters fitting model (used for jump distance plots in the dashboard). |

SSR is computed as follows: <br>
$$\sum_{i=1}^n \left( \hat{y}_{i}-\bar{y})^{2} \right)$$
## TrajectoryList
| Parameter | Type | Description |
| --- | --- | --- |
| filename | TEXT | The filename that contribute to the dataset. |
| trajID | TEXT | The ID used to identify this trajectory. |
| traj_length | INTEGER | The total number of frames this trajectory existed. |
| msd | REAL | The average value of all the tracks' "mean square displacement" in the trajectory. |
| D | REAL | The diffusion coefficient of the trajectory (in Log<sub>10</sub>(&mu;m<sup>2</sup>)). |
| startTime | REAL | The time stamp the trajectory first appear. |
| endTime | REAL | The time stamp the trajectory is last seen. |
| meanX | REAL | The mean X-coordinate of the trajectory. |
| meanY | REAL | The mean Y-coordinate of the trajectory. |
| maxDistance | REAL | The maximum distance a track (that's belong to this trajectory) travelled. |
| meanDistance | REAL | The mean distance a track (that's belong to this trajectory) travelled. |
| medianDistance | REAL | The median distance a track (that's belong to this trajectory) travelled. |

## TrackList
| Parameter | Type | Description |
| --- | --- | --- |
| trajID | TEXT | The ID used to identify this trajectory. |
| Frame | REAL | The time the track is being observed (computed from the frame number it's being detected in and "exposure time"). |
| x | REAL | The X-coordinate of the track at "Frame". |
| y | REAL | The Y-coordinate of the track at "Frame". |
| msd | REAL | The "mean square displacement" of the track with respect to its previous position (in the previous "Frame"). |
| distance | REAL | The distance this track moved with respect to its previous position (in the previous "Frame"). |
| angle | REAL | The angle between the track at "Frame" with respect to its two previous position. |

The angle is calculated by its “diversion” from the previous track (how many degree it branched from previous movement [refer to the Figure below, where the track was moving from “1” to “2” in the first frame and “diverted” to “3” at second frame with the angle theta calculated]).
Note that the angle diversion do not account for whether it's clockwise or anti-clockwise diversion.

## AngleList
| Parameter | Type | Description |
| --- | --- | --- |
| filename | TEXT | The filename that contribute to the dataset. |
| trajID | TEXT | The ID used to identify this trajectory. |
| A1 | INTEGER | Number of angles with tracks between 0 - 10° in this trajectory. |
| A2 | INTEGER | Number of angles with tracks between 10 - 20° in this trajectory. |
| A3 | INTEGER | Number of angles with tracks between 20 - 30° in this trajectory. |
| A4 | INTEGER | Number of angles with tracks between 30 - 40° in this trajectory. |
| A5 | INTEGER | Number of angles with tracks between 40 - 50° in this trajectory. |
| A6 | INTEGER | Number of angles with tracks between 50 - 60° in this trajectory. |
| A7 | INTEGER | Number of angles with tracks between 60 - 70° in this trajectory. |
| A8 | INTEGER | Number of angles with tracks between 70 - 80° in this trajectory. |
| A9 | INTEGER | Number of angles with tracks between 80 - 90° in this trajectory. |
| A10 | INTEGER | Number of angles with tracks between 90 - 100° in this trajectory. |
| A11 | INTEGER | Number of angles with tracks between 100 - 110° in this trajectory. |
| A12 | INTEGER | Number of angles with tracks between 110 - 120° in this trajectory. |
| A13 | INTEGER | Number of angles with tracks between 120 - 130° in this trajectory. |
| A14 | INTEGER | Number of angles with tracks between 130 - 140° in this trajectory. |
| A15 | INTEGER | Number of angles with tracks between 140 - 150° in this trajectory. |
| A16 | INTEGER | Number of angles with tracks between 150 - 160° in this trajectory. |
| A17 | INTEGER | Number of angles with tracks between 160 - 170° in this trajectory. |
| A18 | INTEGER | Number of angles with tracks between 170 - 180° in this trajectory. |

## JDList
| Parameter | Type | Description |
| --- | --- | --- |
| filename | TEXT | The filename that contribute to the dataset. |
| jump_distance | REAL | The jump distance tick (used for jump distance plots in the dashboard). |
| sharedFrequency | REAL | The number of tracks that fall within the "jump_distance" tick (used for jump distance plots in the dashboard). |
| twoParFrequency | REAL | The number of tracks that fall within the "jump_distance" tick based on two parameters fitting (used for jump distance plots in the dashboard). |
| threeParFrequency | REAL | The number of tracks that fall within the "jump_distance" tick based on three parameters fitting (used for jump distance plots in the dashboard). |
| twoParD1Values | REAL | The number of tracks that are "immobile" fall within the "jump_distance" tick based on two parameters fitting (used for jump distance plots in the dashboard). |
| twoParD2Values | REAL | The number of tracks that are "mobile" fall within the "jump_distance" tick based on two parameters fitting (used for jump distance plots in the dashboard). |
| threeParD1Values | REAL | The number of tracks that are "immobile" fall within the "jump_distance" tick based on three parameters fitting (used for jump distance plots in the dashboard). |
| threeParD2Values | REAL | The number of tracks that are "mixed" fall within the "jump_distance" tick based on three parameters fitting (used for jump distance plots in the dashboard). |
| threeParD3Values | REAL | The number of tracks that are "immobile" fall within the "jump_distance" tick based on three parameters fitting (used for jump distance plots in the dashboard). |

# Reference
Previously published algorithms, analysis, and scripts that are utilized in the dashboard can be found below: <br>

## Localization and Tracking:
D. M. McSwiggen et al. (2019) Evidence for DNA-mediated nuclear compartmentalization distinct from phase separation. eLife. 8:e47098. <br>
A. Sergé et al. (2008) Dynamic multiple-target tracing to probe spatiotemporal cartography of cell membranes. Nature methods, 5(8):687. <br>

## MSD-Based Diffusion Plot
J. Chen et al. (2014) Single-molecule dynamics of enhanceosome assembly in embryonic stem cells. Cell. 156(6):1274 - 1285. <br>

## Jump Distance Plot:
D. Mazza et al. (2013) Monitoring dynamic binding of chromatin proteins in vivo by single-molecule tracking. Methods Mol Biol. 1042:117-37. <br>

## Angle Plots:
I. Izeddin et. al. (2014), Single-molecule tracking in live cells reveals distinct target-search strategies of transcription factors in the nucleus. eLife. 3:e02230. <br>

## Heat Map:
J. O. Andrews et al. (2018) qSR: a quantitative super-resolution analysis tool reveals the cell-cycle dependent organization of RNA Polymerase I in live human cells. Sci Rep. 7424 (2018). <br>

## Dwell Time:
A.J. McCann et al. (2021) A dominant-negative SOX18 mutant disrupts multiple regulatory layers essential to transcription factor activity. Nucleic Acids Res. 49(19):10931-10955. Developed by Zhe Liu in Janelia Research Campus.
