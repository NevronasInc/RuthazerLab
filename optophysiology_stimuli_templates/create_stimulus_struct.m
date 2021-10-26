% This script creates a structure with all the stimuli that are presented
% during the experiment.

% There can be different types of stimulations that are defined by the
% codename


stimuli_structure = struct;


Code = 0;
stimuli_structure(Code+1).Code = Code;
stimuli_structure(Code+1).Description = 'Alignment';

Code = 1;
stimuli_structure(Code+1).Code = Code;
stimuli_structure(Code+1).Description = ['Squares. The display area is divided into N (m^2 for some integer m) squares. ' ...
                                                        'Stimulus 1 is the top, left square and stimulus N is the bottom right square.'];

Code = 2;
stimuli_structure(Code+1).Code = Code;
stimuli_structure(Code+1).Description = ['Horizontal and Vertical Bars. There will be N (2m for some integer m) stimuli. ' ...
                                                        'Stimulus 1 is the top-most horizontal bar and stimulus N is the right-most vertical bar.'];

                                                                                                 
Code = 3;
brightness = load('BrightnessLevelStimuli.mat');
stimuli_structure(Code+1).Code = Code;
stimuli_structure(Code+1).Description = ['Brightness levels. N+1 levels of intensity between 0 (black, also null) and 1 (white). ' ...
                                                      'Stimulus 1 is the darkest and stimulus N is brightest.'];
stimuli_structure(Code+1).stimulusID = brightness.stimulusID;
stimuli_structure(Code+1).stimulusMatrix = brightness.stimulusMatrix;


Code = 4;
spatial_frequency = load('SpatialFrequencyStimuli.mat');
stimuli_structure(Code+1).Code = Code;
stimuli_structure(Code+1).Description = ['Spatial frequency. Vertically oriented sinusoidal gratings. ' ...
                                                     'The number of stimuli will be the total number of integer factors of the screen width. ' ...
                                                     'Each stimulus is referred to by the fraction of the screen occupied by a single period, ' ...
                                                     'such that 0.5 is the largest stimulus presented.'];
stimuli_structure(Code+1).stimulusID = spatial_frequency.stimulusID';
stimuli_structure(Code+1).stimulusMatrix = spatial_frequency.stimulusMatrix;


Code = 5;
stimuli_structure(Code+1).Code = Code;
stimuli_structure(Code+1).Description = ['Moving bars. Sinusoidal gratings oriented at N different angles between 0 and 360 degrees, ' ...
                                                        'which move across the screen perpendicular to the orientation.'];


Code = 6;
stimuli_structure(Code+1).Code = Code;
stimuli_structure(Code+1).Description = ['Angled bars. N different bars centered within the display area, ' ...
                                                        'oriented uniformly between 0 and 360 degrees.'];

Code = 7;
stimuli_structure(Code+1).Code = Code;
stimuli_structure(Code+1).Description = ['Circles with varying radii. Disks centered within the display area, ' ...
                                                        'with N+1 different radii uniformly distributed between 0 (also null) ' ...
                                                        'and the screen height divided by two.'];
                                                    
Code = 8;
stimuli_structure(Code+1).Code = Code;
stimuli_structure(Code+1).Description = ['Looming stimuli. Disk moving with constant radius towards fish. For this stimulus, ' ...
                                                        'the file will have a 2x7 array of values. ' ...
                                                        '(1,7) is the apparent speed of the looming and (2,7) is the minimum radius.'];
                                                    
                                                   
Code = 9;
stimuli_structure(Code+1).Code = Code;
stimuli_structure(Code+1).Description = ['Moving spatial frequency. Same as stimulus type 4, but the sinusoidal gratings move ' ...
                                                        'from left to right across the screen.'];                                                    
                                                    
                                              
Code = 10;
stimuli_structure(Code+1).Code = Code;
stimuli_structure(Code+1).Description = ['Blank screen.'];


save('optophysiology_stimulus_templates.mat', 'stimuli_structure')
                                                    
                                                    
                                                    
                                                    