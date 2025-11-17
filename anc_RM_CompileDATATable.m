% Get system user name (under macOS)
user = char(java.lang.System.getProperty('user.name'));
warning('OFF', 'MATLAB:table:RowsAddedExistingVars')

% add tpaths with analysis scripts
addpath(genpath((['/Users/' user '/ownCloud/Shared/MWorks_MatLab'])))
addpath(genpath((['/Users/' user '/ownCloud/Shared/Reversal_Learning/scripts'])))

% set paths for data retrieval and plot saving
data_owncloud = ['/Users/' user '/Desktop/temp_data/'];

% List all sessions for Animals
sessions = dir([data_owncloud '*XBI*']);

% Extract the data for the variables to include
to_include = {'ML_trialStart', ...
    'ML_trialEnd', ...
    'SC_out', ...
    'TRIAL_outcome', ...
    'IO_target', ...
    'IO_distractor', ...
    'IO_neutral1' , ...
    'IO_neutral2', ...
    'EXP_stage', ...
    'EXP_previous_feature', ...
    'EXP_feature', ...
    '#announceMessage', ...
    'fn_stimuliOnScreen'};

files_counter = 1;

Variables = { ...
    'outcome',         'logical';...
    'trial',           'int16';...
    'step',            'int16';...
    'subjID',          'string';...
    'species',         'string';...
    'date',            'string';...
    'time',            'string';...
    'experiment',      'string';...
    'sessionEnd',      'double';...
    'trialStart',      'double';...
    'trialEnd',        'double'};

T = table('Size',[1, size(Variables,1)],...
    'VariableTypes',Variables(:,2),...
    'VariableNames',Variables(:,1));

for ss = 1:length(sessions)
    
    disp(['I am processing: subject datafile ', int2str(files_counter),...
        ' of ', int2str(size(sessions, 1)), ' ', sessions(ss).name])
    
    % Extract data
    data = MW_readFile([data_owncloud sessions(ss).name], ...
        'include', to_include, 'debugLevel', 0);
    trialsID = cell2mat(data.value(data.event == 'TRIAL_start'));
    
    % Extract Staircase, Stage, and Feature for stage information
    A = data.value(data.event == 'SC_out');
    staircase_val = unique([A{:}]);
    
    scID = [A{:}];
    scID_t = data.time(data.event == 'SC_out');
    
    stages = {'discrimination', 'reversal'};
    
    featureID = string(data.value(data.event == 'EXP_previous_feature'));
    featureID_t = data.time(data.event == 'EXP_previous_feature');
    
    % ============================ Fixing bug for rio's session on the 20210203
    broken_sess = isempty(trialsID);
    if broken_sess
        trialStarts = MW_readFile_anc([data_owncloud sessions(ss).name],...
            'include', {'EXP_current_step'});
        trialEnds   = MW_readFile_anc([data_owncloud sessions(ss).name],...
            'include', {'TRIAL_number'});
        
        corrected_t1.value = cell2mat(trialEnds.value);
        corrected_t1.time = trialStarts.time;
        
        corrected_t2.value = cell2mat(trialEnds.value);
        corrected_t2.time = trialEnds.time;
        
        trialsID = cell2mat(trialEnds.value(trialEnds.event == 'TRIAL_number'));
    end
    % =========================================================================
    
    data.value_str = string(data.value);
    
    for i = 1:max(trialsID)
        
        if broken_sess
            t1 = corrected_t1.time(corrected_t1.value == i);
            t2 = corrected_t2.time(corrected_t2.value == i);
        else
            t1 = data.time((data.event == 'TRIAL_start') & ...
                (data.value_str == string(i)));
            t2 = data.time((data.event == 'TRIAL_end') & ...
                (data.value_str == string(i)));
        end
        
        % Only analyse trials longer than 100 ms
        if t2 - t1 > 100
            % Create a temporary table for the given trial (i)
            newT = table('Size',[1, size(Variables,1)],...
                'VariableTypes',Variables(:,2),...
                'VariableNames',Variables(:,1));
            
            % Create an index for the start and end time of the trial
            trial_idx = (data.time > t1) & (data.time <t2);
            
            % Extract stimuli onset based on Target onset
            a = cell2mat(data.value(data.event == 'fn_stimuliOnScreen' & ...
                trial_idx));
            b = data.time(data.event == 'fn_stimuliOnScreen' & trial_idx);
            newT.trialStart = double(b(a == 1));
            newT.trialEnd = t2;
            
            % Store into the temporary table (newT) the date, session, subject
            % and time information from the data file name
            date = split(sessions(ss).name, '_'); % Split the filename
            
            newT.subjID = string(date{1});
            newT.date = date{2};
            newT.time = date{3};
            newT.species = 'rhesus';
            
            % Extract the outcome of the trial
            outcome = data.value((data.event == 'TRIAL_outcome') & trial_idx);
            newT.outcome = sum(ismember(outcome, 'Correct')) > 0;
            
            % Store the time start of the trial and the trial index
            newT.trial = i;
            
            % Extract the staircase output of the trial
            newT.step = scID(find(scID_t <= t2, 1, 'last'));
            
            % Assing the experimental condition
            if newT.step > 10
                newT.experiment = 'experiment';
            else
                newT.experiment = 'AUT';
            end
            
            newT.sessionEnd = data.time(end);
            
            T = vertcat(T,newT);
        end
    end
    
    files_counter = files_counter + 1;
end

% save the table with all data into the DATA.mat
writetable(T,['/Users/acalapai/ownCloud/Shared/XBI_engagement/data/RM_Experiment_1_2_20210831.csv'])
