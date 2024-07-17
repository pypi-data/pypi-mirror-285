function f = visualize_surface(results_volume, template_path, save_path, cmap, vmin, vmax)
    % visualize_surface_multiview Visualize brain connectome data in multiple views.
    %   f = visualize_surface_multiview(results_volume, template, save_path)
    %   This function creates visualizations from multiple viewpoints of the brain and
    %   saves the images if a save path is provided.

    % Define the view positions for different anatomical views
    if isa(results_volume, 'char')
        results_volume = niftiread(results_volume);
    end
    if isa(template_path,'char')
        template = niftiread(template_path);
    end
    if size(template,1) == 193 && size(template,2) == 229 && size(template,3) == 193
        template = template(6:end-6,6:end-6,6:end-6);
    end
    views = {
        struct('Name', 'Mid-Sagittal_Left', 'Position', [0, 0], 'Slice', 'left'),
        struct('Name', 'Mid-Sagittal_Right', 'Position', [180, 0], 'Slice', 'right'),
        struct('Name', 'Lateral_Left_Hemisphere', 'Position', [0, 0], 'Slice', 'none'),
        struct('Name', 'Lateral_Right_Hemisphere', 'Position', [180, 0], 'Slice', 'none'),
        struct('Name', 'Top_View', 'Position', [-90, 90], 'Slice', 'none')
    };

    % Colormap configuration
    if nargin < 5 || isempty(cmap)
        cmap = 'RdBu_r'; % Default colormap
    end
    % vmin and vmax configuration
    if nargin < 5 || isempty(vmin)
        vmin = -4;
    end
    if nargin < 6 || isempty(vmax)
        vmax = 4;
    end

    % Apply the colormap
    if endsWith(cmap, '_r')
        cmap = flip(slanCM(cmap(1:end-2), 1200));
    elseif strcmp(cmap, 'hot')
        cmap = hot(1200);
    else
        cmap = slanCM(cmap, 1200);
    end

    % Iterate through each view, create figures, and save images
    for v = 1:length(views)
        f = figure('Name', views{v}.Name, 'NumberTitle', 'off', 'Renderer', 'opengl', 'Position', [10 10 900 600]);

        % Apply slicing if required
        if strcmp(views{v}.Slice, 'left')
            slicedTemplate = template(floor(end/2)-3:end, :, :);
            slicedResults = results_volume(floor(end/2)-3:end, :, :);
        elseif strcmp(views{v}.Slice, 'right')
            slicedTemplate = template(1:floor(end/2)+2, :, :);
            slicedResults = results_volume(1:floor(end/2)+2, :, :);
        else
            slicedTemplate = template;
            slicedResults = results_volume;
        end

        % Compute isosurface
        [pt, vt, ct] = isosurface(slicedTemplate, slicedResults);

        % Filtering groups
        g = tesgroup(pt);
        [~, max_g] = max(sum(g, 1));
        m = sum(g(:, [1:(max_g-1), (max_g+1):end]), 2) == 0;
        pt = pt(m, :);

        % Plot the surface
        p = patch('Vertices', vt, 'Faces', pt, ...
                  'FaceVertexCData', ct, ...
                  'FaceColor', 'flat', ...
                  'EdgeColor', 'none', ...
                  'FaceAlpha', 1);

        % Set the axis properties
        axis vis3d;
        axis equal;
        axis off;
        colormap(cmap);
        clim([vmin vmax]);  % Adjust based on your data needs

        % Adjust lighting properties
        p.FaceLighting = 'gouraud';
        p.EdgeLighting = 'gouraud';
        p.BackFaceLighting = 'unlit';
        p.SpecularColorReflectance = 0.1;
        p.SpecularExponent = 100;
        p.SpecularStrength = 0;

        % Set the view and lighting
        view(views{v}.Position);
        lightangle(views{v}.Position(1), views{v}.Position(2));

        % Add a colorbar
        colorbar;

        % Save the figure if save path is provided
        if nargin > 2 && ~isempty(save_path)
            img_filename = fullfile(save_path, [views{v}.Name, '.png']);
            print(f, img_filename, '-dpng','-r500');
            fprintf('Saved %s\n', img_filename);
        end

        close(f); % Close the figure after saving to avoid GUI clutter
    end
end
