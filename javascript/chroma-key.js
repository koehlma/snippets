/*
 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.
 
 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.
 
 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/

/*
Some fancy HTML5 Video and Javascript fun.
Uses a hue color and a variance to do some chroma keying.

Usage:
    HTML:
        <!-- hidden video element -->
        <video id="video" controls="hidden" src="file.mp4" style="display: none;"></video>
        <!-- hidden buffer canvas, height and width should be the video's height and width-->
        <canvas id="buffer" height="800" width="480" style="display: none;"></canvas>
        <!-- output canvas - rendering happens here, height and width should be the video's height and width -->
        <canvas id="output" height="800" width="480" style=""></canvas>
    
    Javascript:
        var video = document.getElementById('video')
        var chroma_key = new ChromaKey(video, document.getElementById('buffer'), document.getElementById('output'), 120, 35, 0);
        video.controls = false; // hide the controls
        video.play(); // because the video element is hidden we need to start the video manually   
*/

function ChromaKey(video, buffer, output, color, variance, blur_radius) {
    this.video = video;
    this.buffer_canvas = buffer;
    this.buffer = buffer.getContext('2d');
    this.output_canvas = output;
    this.output = output.getContext('2d');
    this.color = color;
    this.variance = variance;
    this.blur_radius = blur_radius;
    
    var me = this;
    
    video.chroma_key = this;
    video.addEventListener('play', function() {me.start()}, false);
    video.addEventListener('ended', function() {me.stop()}, false);
    video.addEventListener('pause', function() {me.stop()}, false);
    video.addEventListener('abort', function() {me.stop()}, false);
    video.addEventListener('error', function() {me.stop()}, false);
}

ChromaKey.prototype.rgb2hue = function(red, green, blue) {
    var red = red / 255;
    var green = green / 255;
    var blue = blue / 255;
    var maximum = Math.max(red, green, blue);
    var minimum = Math.min(red, green, blue);
    if (maximum == minimum) {
        return [0, 0, 0];
    } else if (maximum == red) {
        hue = 60 * ((green - blue) / (maximum - minimum));
    } else if (maximum == green) {
        hue = 60 * (2 + (blue - red) / (maximum - minimum));
    } else {
        hue = 60 * (4 + (red - green) / (maximum - minimum));
    }
    if (hue < 0) {
        hue += 360;
    }
    if (maximum == 0) {
        saturation = 0;
    } else {
        saturation = (maximum - minimum) / maximum;
    }
    return [hue, saturation, maximum];
}

ChromaKey.prototype.start = function() {
    var me = this;
    
    this.interval = setInterval(function() {me.process_frame()}, 30);
}

ChromaKey.prototype.stop = function() {
    clearInterval(this.interval);
}

ChromaKey.prototype.process_frame = function() {
    this.buffer.drawImage(this.video, 0, 0);
    var frame = this.buffer.getImageData(0, 0, this.output_canvas.width, this.output_canvas.height);
    var lenght = frame.data.length;
    for (index = 0; index < lenght; index += 4) {
        hue = this.rgb2hue(frame.data[index], frame.data[index + 1], blue = frame.data[index + 2])[0];
        if ((this.color - this.variance) < hue && hue < (this.color + this.variance)) {
            frame.data[index + 3] = 0;
        } else {
            frame.data[index + 3] = 255;
        }
    }
    if (this.blur_radius > 0) {
        this.blur_alpha(frame, this.output_canvas.width, this.output_canvas.height, this.blur_radius);
    }
    this.output.putImageData(frame, 0, 0);
}

ChromaKey.prototype.blur_alpha = function(frame, width, height, radius) {
    // this is to slow for realtime rendering
    var row_width, total, count, new_row, new_col;
    for (row = 0; row < height; row++) {
        row_width = row * width;
        for (col = 0; col < width; col++) {
            total = 0;
            count = 0;
            for (distance_row = -radius; distance_row <= radius; distance_row++) {
                new_row = row_width + distance_row * width;
                if (new_row > -1) {
                    for (distance_col = -radius; distance_col <= radius; distance_col++) {
                        new_col = col + distance_col
                        if (new_col > -1) {
                            total += frame.data[(new_row + new_col) * 4 + 3];
                            count += 1;
                        }
                    }
                }
            }
            frame.data[(row_width + col) * 4 + 3] = total / count;
        }
    }
    return frame;
}