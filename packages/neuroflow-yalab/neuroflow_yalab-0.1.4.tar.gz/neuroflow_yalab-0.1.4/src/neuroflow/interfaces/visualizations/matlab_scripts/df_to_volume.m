function results_map = df_to_volume(values, atlas_path)
    %df_to_volume Create a map of results overlaid on an atlas.
    %   results_map= df_to_volume(values, atlas_path, template_path)
    %   takes the file paths for an atlas and a template image along with
    %   a values vector, and overlays the results onto the atlas based on    %   the indices defined in the atlas.

    %atlas_path = '/home/galkepler/Downloads/space-MNI152_atlas-huang2022_res-1mm_dseg.nii';
    %template_path = '/home/galkepler/Downloads/MNI152_T1_1mm_brain.nii'; %MNI
    %results = P; %load(''); % 1Xn
    atlas = niftiread(atlas_path);
    N = max(atlas(:));  %
    results_map = zeros(size(atlas));
    for ind=1:N
        if ~isnan(values(ind))
            results_map(atlas==ind) = values(ind);
        end
    end


%template(size(template,1)/2:end,:,:) = 0; % for mid-sagittal
