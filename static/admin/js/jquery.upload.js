


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
		( ( B00011111 & c		  ) <<  6 ) |
		( ( B00111111 & data[i++] ) <<  0 )
		);
	} else if ( ( c < B11110000 ) ) {
		result += String.fromCharCode(
		( ( B00001111 & c         ) << 12 ) |
		( ( B00111111 & data[i++] ) <<  6 ) |
		( ( B00111111 & data[i++] ) <<  0 )
		);
	} else if ( ( c < B11111000 ) ) {
		result += String.fromCharCode(
		( ( B00000111 & c         ) << 18 ) |
		( ( B00111111 & data[i++] ) << 12 ) |
		( ( B00111111 & data[i++] ) <<  6 ) |
		( ( B00111111 & data[i++] ) <<  0 )
		);
	} else if ( ( c < B11111100 ) ) {
		result += String.fromCharCode(
		( ( B00000011 & c		  ) << 24 ) |
		( ( B00111111 & data[i++] ) << 18 ) |
		( ( B00111111 & data[i++] ) << 12 ) |
		( ( B00111111 & data[i++] ) <<  6 ) |
		( ( B00111111 & data[i++] ) <<  0 )
		);
	} else if ( ( c < B11111110 ) ) {
		result += String.fromCharCode(
		( ( B00000001 & c		  ) << 30 ) |
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

/////////////////////////////////////////////////////////////////////////////////////////////

(function($) {
	var as = $.ajaxSettings;
	
	$.xhr = {
		registry: {
			xhr: as.xhr	
		},
		register:function( name, fn ){
			this.registry[name] = fn;
		}
	};
	
	// The built-in method is used by default
	// To set another one as default, use $.ajaxSetup({ transport:'my_xhr' })
	as.transport = 'xhr';
	
	// This handler is used instead, don't override it
	as.xhr = function(){
		return $.xhr.registry[ this.transport ]( this );
	};
	
	$.extend({
		// 用ajax 上传文件，目前只支持 Firefox 3.5+ // TODO: 使用 FormData 添加对 WebKit支持，参见 http://jquery-html5-upload.googlecode.com/
		upload: function( url, files, data, callback, type, onProgress, onFinish ) {
			// shift arguments if data argument was omited
			if ( $.isFunction( data ) ) {
				type = type || callback;
				callback = data;
				data = {};
			}
			var settings = {
				type: "POST",
				url: url,
				data: data,
				success: callback,
				dataType: type
			};
			//console.log(settings);
			if (files.length > 0 ) {
				var boundary = '----sp-boundary' + parseInt(Math.random()*(2 << 16)), dash = '--', crlf = '\r\n', blob = '';

				function buildBlob(boundary, files, data) {
					$.each(data, function(i, item) {
						blob += dash + boundary + crlf +
							'Content-Disposition: form-data; name="' + item.name + '"' + crlf + crlf;
						blob += (typeof item.value == "string" ? char2str(str2utf8(item.value)) : item.value) + crlf;
					});
					// Build RFC2388 blob
					$.each(files, function(i, file) {
						var name = (typeof file.id === "string" ? file.id : 'file'+i);
						blob += dash + boundary + crlf +
							'Content-Disposition: form-data; name="' + name;
						if (typeof file.name !== "undefined" && file.name !== '') {
							blob += '"; filename="' + char2str(str2utf8(file.name)) + '"' + crlf +
								'Content-Type: ' + file.type + crlf + crlf +
								file.getAsBinary() + crlf;
						} else { // 允许空着，占位
							blob += '"; filename=""' + crlf +
								'Content-Type: application/octet-stream ' + crlf + crlf +
								'' + crlf;
						}
					});
					blob += dash + boundary + dash + crlf;
					return blob;
				}

				var xhr = new XMLHttpRequest();
				if (xhr.sendAsBinary) {
					xhr.send = function (data) {
						return xhr.sendAsBinary(data);
					};
				}
				if( $.isFunction(onProgress) ) {
					xhr.upload.addEventListener("progress", function(e) {
						if (e.lengthComputable) {
							var percentage = Math.round((e.loaded * 100) / e.total);
							//console.log(percentage);
							onProgress.call(this, percentage);
						}
					}, false);
				}
				if( $.isFunction(onFinish) ) {
					xhr.upload.addEventListener("load", function(e){
						// 100% complete
						onFinish.call(this);
					}, false);
				}

				$.xhr.register( 'upload_xhr', function( settings ){
					return xhr;
				});
				settings.transport = 'upload_xhr'

				settings.data = buildBlob(boundary, files, data);
				//console.log(data);
				settings.contentType = 'multipart/form-data; boundary=' + boundary;

			}
			//console.log(blob);
			/*var xhr = new XMLHttpRequest(); 	//$.ajaxSettings.xhr();
			xhr.open("POST", settings.url, true);
			xhr.setRequestHeader('Content-Type', settings.contentType);
			xhr.setRequestHeader('Content-Length', blob.length);
			function statusHandler() {
				console.log(xhr.readyState);
			}
			xhr.overrideMimeType('text/plain; charset=x-user-defined-binary');
			xhr.sendAsBinary(blob);*/ // 
			return $.ajax(settings);
		}

	});
	$.fn.editable = function(target, options) {
		
	};

	/**
	 * example: <div id="land_box"></div>
	 * $('#land_box').radioButtons({data: Catalog.all.land, name: 'land'});
	 */
	$.fn.radioButtons = function(options) {
		options = $.extend({
			data: {'0':'Choice 1','1':'Choice 2'},
			name: 'radio',
			selected: '',
			skipEmpty: true
		}, options);
		var self = $(this).empty(), i = 0;
		for( var k in options.data) {
			if (options.skipEmpty && k === "") continue;
			var id = 'ws_'+options.name+'_'+i, text = options.data[k], radio =
			$("<input />").attr("id", id)
				.attr("type", "radio").attr("name", options.name)
				.attr("value", k);
			if (k === options.selected) radio.attr('checked', 'checked');
			radio.appendTo(self);
			$("<label />").attr("for", id).text(text).appendTo(self);
			i ++;
		}
		self.buttonset();
		return this;
	};
	
	$.expr[':'].range = function(el) {
		var type = el.getAttribute("type");
		return type && type == 'range' || !!$(el).filter("input").data("rangeinput");
	};
	
	$.fn.rangeInput = function(options) {
		options = $.extend({
			min: 1,
			max: 100,
			step: 1,
			value: 50,
			range: 'min'
		}, options);
		var input = $(this), slider = $('<div class="range-slider"></div>').insertBefore(input).slider({
			min: options.min,
			max: options.max,
			step: options.step,
			range: options.range,
			value: options.value,
			slide: function(event, ui) {
				input.val(ui.value - 1);
			}
		});
		input.change(function() {
			slider.slider("value", this.value);
		}).addClass('range').val(options.value);
		
	};
})(jQuery);
