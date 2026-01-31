# How to Add Videos to GitHub README

The videos in the KLAM README are embedded using GitHub's native video support. Here's how to update or add new demonstration videos:

## Method 1: Using GitHub Issues (Recommended)

1. **Upload the video to a GitHub issue**:
   - Go to your repository's Issues tab
   - Create a new issue (or use an existing one)
   - Drag and drop your `.mp4` file into the comment box
   - GitHub will automatically upload it and generate a URL like:
     ```
     https://github.com/user-attachments/assets/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx/demo.mp4
     ```

2. **Copy the generated URL**:
   - Once uploaded, GitHub shows the markdown embed code
   - Copy the URL (just the URL, not the whole markdown)

3. **Update README.md**:
   - Replace the placeholder URL in the README with your actual URL
   - Example:
     ```markdown
     https://github.com/user-attachments/assets/your-actual-video-id/demo.mp4
     ```

4. **Close the issue** (if you created a temporary one)

## Method 2: Commit Videos to Repository

1. **Place videos in the docs folder**:
   ```bash
   cp your_video.mp4 docs/demo_video.mp4
   ```

2. **Add and commit**:
   ```bash
   git add docs/demo_video.mp4
   git commit -m "Add demonstration video"
   git push
   ```

3. **Use relative path in README**:
   ```markdown
   https://user-images.githubusercontent.com/YOUR_USER_ID/demo_video.mp4
   ```

## Video Requirements

- **Format**: MP4 (H.264 codec recommended)
- **Size**: Max 10MB for best performance
- **Recommended resolution**: 1280x720 or 1920x1080
- **Frame rate**: 30 FPS

## Current Videos

- `demo_run_project.mp4` - Shows how to run KLAM
- `demo_add_files.mp4` - Shows how to add files to the project

Both videos are currently stored in the `docs/` folder.
