

(function($){
	/////////////////////////////////////////////////////////////////////////////////////////////

	var B10000000 = 0x80;
	var B11000000 = 0xC0;
	var B11100000 = 0xE0;
	var B11110000 = 0xF0;
	var B11111000 = 0xF8;
	var B11111100 = 0xFC;
	var B11111110 = 0xFE;
	var B01111111 = 0x7F;
	var B00111111 = 0x3F;
	var B00011111 = 0x1F;
	var B00001111 = 0x0F;
	var B00000111 = 0x07;
	var B00000011 = 0x03;
	var B00000001 = 0x01;

	function str2utf8( str ){
		var result = [];
		var length = str.length;
		var idx=0;
		for ( var i=0; i<length; i++ ){
		var c = str.charCodeAt( i );
		if ( c <= 0x7f ) {
			result[idx++] = c;
		} else if ( c <= 0x7ff ) {
			result[idx++] = B11000000 | ( B00011111 & ( c >>>  6 ) );
			result[idx++] = B10000000 | ( B00111111 & ( c >>>  0 ) );
		} else if ( c <= 0xffff ) {
			result[idx++] = B11100000 | ( B00001111 & ( c >>> 12 ) ) ;
			result[idx++] = B10000000 | ( B00111111 & ( c >>>  6 ) ) ;
			result[idx++] = B10000000 | ( B00111111 & ( c >>>  0 ) ) ;
		} else if ( c <= 0x10ffff ) {
			result[idx++] = B11110000 | ( B00000111 & ( c >>> 18 ) ) ;
			result[idx++] = B10000000 | ( B00111111 & ( c >>> 12 ) ) ;
			result[idx++] = B10000000 | ( B00111111 & ( c >>>  6 ) ) ;
			result[idx++] = B10000000 | ( B00111111 & ( c >>>  0 ) ) ;
		} else {
			throw "error";
		}
		}
		return result;
	}

	function utf82str( data ) {
		var result = "";
		var length = data.length;

		for ( var i=0; i<length; ){
		var c = data[i++];
		if ( c < 0x80 ) {
			result += String.fromCharCode( c );
		} else if ( ( c < B11100000 ) ) {
			result += String.fromCharCode(
			( ( B00011111 & c		) <<  6 ) |
			( ( B00111111 & data[i++] ) <<  0 )
			);
		} else if ( ( c < B11110000 ) ) {
			result += String.fromCharCode(
			( ( B00001111 & c	) << 12 ) |
			( ( B00111111 & data[i++] ) <<  6 ) |
			( ( B00111111 & data[i++] ) <<  0 )
			);
		} else if ( ( c < B11111000 ) ) {
			result += String.fromCharCode(
			( ( B00000111 & c	) << 18 ) |
			( ( B00111111 & data[i++] ) << 12 ) |
			( ( B00111111 & data[i++] ) <<  6 ) |
			( ( B00111111 & data[i++] ) <<  0 )
			);
		} else if ( ( c < B11111100 ) ) {
			result += String.fromCharCode(
			( ( B00000011 & c		) << 24 ) |
			( ( B00111111 & data[i++] ) << 18 ) |
			( ( B00111111 & data[i++] ) << 12 ) |
			( ( B00111111 & data[i++] ) <<  6 ) |
			( ( B00111111 & data[i++] ) <<  0 )
			);
		} else if ( ( c < B11111110 ) ) {
			result += String.fromCharCode(
			( ( B00000001 & c		) << 30 ) |
			( ( B00111111 & data[i++] ) << 24 ) |
			( ( B00111111 & data[i++] ) << 18 ) |
			( ( B00111111 & data[i++] ) << 12 ) |
			( ( B00111111 & data[i++] ) <<  6 ) |
			( ( B00111111 & data[i++] ) <<  0 )
			);
		}
		}
		return result;
	}
	/////////////////////////////////////////////////////////////////////////////////////////////

	// convert unicode character array to string
	function char2str( ca ) {
		var result = "";
		for ( var i=0; i<ca.length; i++ ) {
		result += String.fromCharCode( ca[i] );
		}
		return result;
	}

	// convert string to unicode character array
	function str2char( str ) {
		var result = new Array( str.length );
		for ( var i=0; i<str.length; i++ ) {
		result[i] = str.charCodeAt( i );
		}
		return result;
	}
	
	// image drop box support
	
	jQuery.event.props.push("dataTransfer");
	
	var opts = {},
		default_opts = {
			url: '',
			refresh: 1000,
			field_id: '',
			field_name: 'userfile',
			maxfiles: 25,		   // Ignored if queuefiles is set > 0
			maxfilesize: 1,		 // MB file size limit
			queuefiles: 0,		  // Max files before queueing (for large volume uploads)
			queuewait: 200,		 // Queue wait time if full
			data: {},
			headers: {},
			drop: empty,
			dragEnter: empty,
			dragOver: empty,
			dragLeave: empty,
			docEnter: empty,
			docOver: empty,
			docLeave: empty,
			beforeEach: empty,
			afterAll: empty,
			rename: empty,
			error: function(err, file, i) {
				alert(err);
			},
			createImage: empty,
			imageLoaded: empty,
			uploadStarted: empty,
			uploadFinished: empty,
			progressUpdated: empty,
			speedUpdated: empty
		},
		errors = ["BrowserNotSupported", "TooManyFiles", "FileTooLarge", "UnselectFile"],
		doc_leave_timer, stop_loop = false,
		images,
		files_count = 0,
		files;

	$.fn.imgdrop = function(options) {
		opts = $.extend( {}, default_opts, options );
		// 经测试发现：Firefox 13 dragLeave 事件不支持了, 貌似从4开始就不支持了
		
		this.bind('drop', drop).bind('dragenter', dragEnter).bind('dragover', dragOver).bind('dragleave', dragLeave);
		$(document).bind('drop', docDrop).bind('dragenter', docEnter).bind('dragover', docOver).bind('dragleave', docLeave);
		$('#' + opts.field_id).change(function(e) {
			opts.drop(e);
			files = e.target.files;
			files_count = files.length;
			preview(files);
		});
	};
	
	function drop(e) {//log('drop');
		opts.drop(e);
		files = e.dataTransfer.files;
		files_count = files.length;
		//upload();
		preview(files);
		e.preventDefault();
		return false;
	}
	
	function preview (files) {
		if (files === null || files === undefined) {
			opts.error(errors[0]);
			return false;
		}
		
		stop_loop = false;
		if (!files) {
			opts.error(errors[3]);
			return false;
		}
		
		files_count = files.length;
		for (var i=0; i<files_count; i++) {
			if (stop_loop) return false;
			createImage(files[i]);
		}
	}

	function prettysize(bytes){	// simple function to show a friendly size
		var i = 0;
		while(1023 < bytes){
			bytes /= 1024;
			++i;
		};
		return  i ? bytes.toFixed(2) + ["", " Kb", " Mb", " Gb", " Tb"][i] : bytes + " bytes";
	}

	function createImage (file) {
		var imageType = /image.*/;
		if (!file.type.match(imageType)) return false;
		var img = document.createElement("img");
		img.file = file;
		opts.createImage(img);
		var reader = new FileReader();
		reader.onload = (function(img) {
			return function(e) {
				img.src = e.target.result;
				$(img).attr('title',''+img.naturalWidth+'x'+img.naturalHeight+', '+prettysize(img.file.size));
				opts.imageLoaded(img);
			};
		})(img);
		reader.readAsDataURL(file);
	}
	
	function dragEnter(e) {//log('dragEnter');
		clearTimeout(doc_leave_timer);
		e.preventDefault();
		opts.dragEnter(e);
	}
	
	function dragOver(e) {//log('dragOver');
		clearTimeout(doc_leave_timer);
		e.preventDefault();
		opts.docOver(e);
		opts.dragOver(e);
	}

	function dragLeave(e) {//log('dragLeave');
		clearTimeout(doc_leave_timer);
		opts.dragLeave(e);
		e.stopPropagation();
	}

	function docDrop(e) {//log('docDrop');
		e.preventDefault();
		opts.docLeave(e);
		return false;
	}

	function docEnter(e) {//log('docEnter');
		clearTimeout(doc_leave_timer);
		e.preventDefault();
		opts.docEnter(e);
		return false;
	}

	function docOver(e) {//log('docOver');
		clearTimeout(doc_leave_timer);
		e.preventDefault();
		opts.docOver(e);
		return false;
	}

	function docLeave(e) {//log('docLeave');
		doc_leave_timer = setTimeout(function(){
			opts.docLeave(e);
		}, 200);
	}

	function empty(){}

	// start upload statement

	function beforeEach(file) {
		return opts.beforeEach(file);
	}

	function afterAll() {
		return opts.afterAll();
	}

	function getIndexBySize(size) {
		for (var i = 0; i < files_count; i++) {
			if (files[i].size == size) {
				return i;
			}
		}

		return undefined;
	}

	function progress(e) { // xhr.upload event: progress
		if (e.lengthComputable) {
			var percentage = Math.round((e.loaded * 100) / e.total);
			
			if (this.currentProgress != percentage) {

				this.currentProgress = percentage;
				if (this.ctrl) {
					this.ctrl.update(this.currentProgress);
				}
				opts.progressUpdated(this.index, this.file, this.currentProgress);

				var elapsed = new Date().getTime();
				var diffTime = elapsed - this.currentStart;
				if (diffTime >= opts.refresh) {
					var diffData = e.loaded - this.startData;
					var speed = diffData / diffTime; // KB per second
					opts.speedUpdated(this.index, this.file, speed);
					this.startData = e.loaded;
					this.currentStart = elapsed;
				}
			}
		}
	}

	// Respond to an upload
	function upload() {
		if (arguments.length > 0 && $.isPlainObject(arguments[0])) {
			opts = $.extend( {}, default_opts, opts, arguments[0] );
			if (opts.files) {
				files = opts.files;
				files_count  = files.length;
			}
			if (opts.images) {
				images = opts.images;
			}
		}

		stop_loop = false;

		if (!files) {log(files);
			opts.error(errors[3]);
			return false;
		}

		var filesDone = 0,
			filesRejected = 0;

		if (files_count > opts.maxfiles && opts.queuefiles === 0) {
			opts.error(errors[1]);
			return false;
		}

		// Define queues to manage upload process
		var workQueue = [];
		var processingQueue = [];
		var doneQueue = [];

		// Add everything to the workQueue
		for (var i = 0; i < files_count; i++) {
			workQueue.push(i);
		}

		// Helper function to enable pause of processing to wait
		// for in process queue to complete
		var pause = function(timeout) {
				setTimeout(process, timeout);
				return;
		}

		// Process an upload, recursive
		var process = function() {

				var fileIndex;

				if (stop_loop) return false;

				// Check to see if are in queue mode
				if (opts.queuefiles > 0 && processingQueue.length >= opts.queuefiles) {

					return pause(opts.queuewait);

				} else {

					// Take first thing off work queue
					fileIndex = workQueue[0];
					workQueue.splice(0, 1);

					// Add to processing queue
					processingQueue.push(fileIndex);

				}

				try {
					if (beforeEach(files[fileIndex]) != false) {
						if (fileIndex === files_count) return;
						var reader = new FileReader(),
							max_file_size = 1024 * opts.maxfilesize;

						reader.index = fileIndex;
						if (files[fileIndex].size > max_file_size) {
							opts.error(errors[2], files[fileIndex], fileIndex);
							// Remove from queue
							processingQueue.forEach(function(value, key) {
								if (value === fileIndex) processingQueue.splice(key, 1);
							});
							filesRejected++;
							return true;
						}
						if (images.length == files_count) {
							reader.img = images[fileIndex];
						}
						reader.onloadend = send;
						reader.readAsBinaryString(files[fileIndex]);

					} else {
						filesRejected++;
					}
				} catch (err) {
					log(err);
					// Remove from queue
					processingQueue.forEach(function(value, key) {
						if (value === fileIndex) processingQueue.splice(key, 1);
					});
					opts.error(errors[0]);
					return false;
				}

				// If we still have work to do,
				if (workQueue.length > 0) {
					process();
				}

			};

		var send = function(e) { // FileReader event: loadend

			var fileIndex = ((typeof(e.srcElement) === "undefined") ? e.target : e.srcElement).index

			// Sometimes the index is not attached to the
			// event object. Find it by size. Hack for sure.
			if (e.target.index == undefined) {
				e.target.index = getIndexBySize(e.total);
			}

			if (e.target.img) {
				this.ctrl = createThrobber(e.target.img);
			}
			var self = this;

			var xhr = new XMLHttpRequest(),
					upload = xhr.upload,
					file = files[e.target.index],
					index = e.target.index,
					start_time = new Date().getTime(),
					boundary = '------multipartformboundary' + (new Date).getTime(),
					binary;

			binary = buildBlob(boundary, file, e.target.result);

			if (this.ctrl) upload.ctrl = this.ctrl;
			upload.index = index;
			upload.file = file;
			upload.downloadStartTime = start_time;
			upload.currentStart = start_time;
			upload.currentProgress = 0;
			upload.startData = 0;
			upload.addEventListener("progress", progress, false);

			xhr.open("POST", opts.url, true);
			xhr.setRequestHeader('content-type', 'multipart/form-data; boundary=' + boundary);

			// Add headers
			$.each(opts.headers, function(k, v) {
				xhr.setRequestHeader(k, v);
			});

			xhr.sendAsBinary(binary);

			opts.uploadStarted(index, file, files_count);

			xhr.onload = function() {
				if (xhr.responseText) {
					var now = new Date().getTime(),
							timeDiff = now - start_time,
							result = opts.uploadFinished(index, file, jQuery.parseJSON(xhr.responseText), timeDiff, xhr);
					filesDone++;
					//log('self:', typeof self, typeof this, typeof self.ctrl)
					if (self.ctrl) {
						self.ctrl.update(100);
						var canvas = self.ctrl.ctx.canvas;
						canvas.parentNode.removeChild(canvas);
					}

					// Remove from processing queue
					processingQueue.forEach(function(value, key) {
						if (value === fileIndex) processingQueue.splice(key, 1);
					});

					// Add to donequeue
					doneQueue.push(fileIndex);

					if (filesDone == files_count - filesRejected) {
						afterAll();
					}
					if (result === false) stop_loop = true;
				}
			};

		}

		// Initiate the processing loop
		process();

	}
	
	//var boundary = '----sp-boundary' + parseInt(Math.random()*(2 << 16));
	function buildBlob(boundary, file, content) {//log(file)
		var dash = '--', crlf = '\r\n', blob = '';
		
		if (opts.data) {
			$.each(opts.data, function(i, item) {
				blob += dash + boundary + crlf +
					'Content-Disposition: form-data; name="' + item.name + '"' + crlf + crlf;
				blob += (typeof item.value == "string" ? char2str(str2utf8(item.value)) : item.value) + crlf;
			});
		}
		
		
		var name = (typeof file.id === "string" ? file.id : opts.field_name);
		if (typeof file.index !== "undefined") {
			blob += dash + boundary + crlf + 
				'Content-Disposition: form-data; name="' + name + '_index' + '"' + crlf + crlf;
			blob += file.index + crlf;
		}
		if (typeof file.label === "string") {
			blob += dash + boundary + crlf + 
				'Content-Disposition: form-data; name="' + name + '_label' + '"' + crlf + crlf;
			blob += char2str(str2utf8(file.label)) + crlf;
		}
		
		blob += dash + boundary + crlf +
			'Content-Disposition: form-data; name="' + name;
		if (typeof file.name !== "undefined" && file.name !== '') {
			blob += '"; filename="' + char2str(str2utf8(file.name)) + '"' + crlf +
				'Content-Type: ' + file.type + crlf + crlf + content + crlf;
		} else { // 允许空着，占位
			blob += '"; filename=""' + crlf +
				'Content-Type: application/octet-stream ' + crlf + crlf + '' + crlf;
		}
		
		blob += dash + boundary + dash + crlf;
		return blob;
	}

	function createThrobber(img) {
		var offset = $(img).offset(), x = offset.left, y = offset.top;
		//var x = img.x;
		//var y = img.y;

		var canvas = document.createElement("canvas");
		img.parentNode.appendChild(canvas);
		canvas.width = img.width;
		canvas.height = img.height;
		var size = Math.min(canvas.height, canvas.width);
		canvas.style.top = y + "px";
		canvas.style.left = x + "px";
		canvas.classList.add("throbber");
		var ctx = canvas.getContext("2d");
		ctx.textBaseline = "middle";
		ctx.textAlign = "center";
		ctx.font = "15px monospace";
		ctx.shadowOffsetX = 0;
		ctx.shadowOffsetY = 0;
		ctx.shadowBlur = 14;
		ctx.shadowColor = "white";

		var ctrl = {};
		ctrl.ctx = ctx;
		ctrl.update = function(percentage) {
			var ctx = this.ctx;
			ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);
			ctx.fillStyle = "rgba(0, 0, 0, " + (0.8 - 0.8 * percentage / 100)+ ")";
			ctx.fillRect(0, 0, ctx.canvas.width, ctx.canvas.height);
			ctx.beginPath();
			ctx.arc(ctx.canvas.width / 2, ctx.canvas.height / 2,
					size / 6, 0, Math.PI * 2, false);
			ctx.strokeStyle = "rgba(255, 255, 255, 1)";
			ctx.lineWidth = size / 10 + 4;
			ctx.stroke();
			ctx.beginPath();
			ctx.arc(ctx.canvas.width / 2, ctx.canvas.height / 2,
					size / 6, -Math.PI / 2, (Math.PI * 2) * (percentage / 100) + -Math.PI / 2, false);
			ctx.strokeStyle = "rgba(0, 0, 0, 1)";
			ctx.lineWidth = size / 10;
			ctx.stroke();
			ctx.fillStyle = "white";
			ctx.baseLine = "middle";
			ctx.textAlign = "center";
			ctx.font = "10px monospace";
			ctx.fillText(percentage + "%", ctx.canvas.width / 2, ctx.canvas.height / 2);
		}
		ctrl.update(0);
		return ctrl;
	}
	
	
	// image upload
	$.extend({
		prettysize: prettysize,
		imgpreview: preview,
		imgupload: upload
	});

	try {
		if (!XMLHttpRequest.prototype.sendAsBinary) {
			XMLHttpRequest.prototype.sendAsBinary = function(datastr) {
			function byteValue(x) {
				return x.charCodeAt(0) & 0xff;
			}
			var ords = Array.prototype.map.call(datastr, byteValue);
			var ui8a = new Uint8Array(ords);
			this.send(ui8a.buffer);
			}
		}		
	} catch (e) {log(e)}

})(jQuery);