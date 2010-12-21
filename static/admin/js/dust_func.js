
if (!this.Dust) {
	var Dust = {};
}
(function($$, $){
	$$.extend = function (destination, source, callback) {
		for (var property in source)
		  destination[property] = source[property];
		if($$.dev) destination['__noSuchMethod__'] = function (prop, args){ error(prop, " : no such method exists", args); };
		if ($.isFunction(callback)) callback();
		return destination;
	};
	$$.cache = {};
	$$.extend(window, {
		log: ($$.dev && window.console) ? function() { console.log.apply(console, arguments); } : function() { },
		error: ($$.dev && window.console) ? function() { console.error.apply(console, arguments); } : function() { },
		dir: ($$.dev && window.console) ? function(a) { console.dir(a); } : function() { },
		info: ($$.dev && window.console) ? function(a) { console.info(a); } : function() { },
	}, function(){
		log("logging enabled");
		log("Window object extended");
	});

	
	$$.extend($$, {

		alert: function(message, title, callback){
			if ($.isFunction(title)) {
				callback = title;
				title = false;
			}
			title = title || "提示!";
			$('body').append('<div id="dialog" class=" ui-corner-all" title="'+title+'" style="display:none;">\
						<span class="ui-icon ui-icon-alert" style="float:left; margin:7px 7px 50px 0;"></span><p style="display:block;float:left;">'+message.replace(/\n/g,"<br />\n")+'</p></div>');
			$("#dialog").dialog({
	  			bgiframe: false,
	  			modal: false,
	  			closeOnEscape: true,
	  			close: function(){
					$('#dialog').remove();
					if ($.isFunction(callback)) callback();
	  			},
	  			buttons: {
	  				Ok: function() {
						$(this).dialog('close');
	  				}
	  			}
	  		});
		},
		confirm: function(title, message, callback, falseCallBack, height, width){
			if(title == null) title = "确认";
			if(message == null) message = "Are you sure want to proceed ?";
			$('body').append('<div id="dialog" style="display:none;" title="'+title+'">\
						<p><span class="ui-icon ui-icon-info" style="float:left; margin:0 7px 20px 0;"></span>'+message.replace("\n","<br />\n")+'</p></div>');
			$("#dialog").dialog({
	  			bgiframe: true,
	  			resizable: false,
	  			height: height,
	  			width: width,
	  			modal: false,
	  			overlay: {
	  				backgroundColor: '#000',
	  				opacity: 0.5
	  			},
	  			closeOnEscape: true,
	  			dialogClass: 'confirm',
	  			close: function(){
	  			  $(this).dialog('destroy');
	  			  $('#dialog').remove();
	  			},
	  			buttons: {
	  				'Ok': function() {
	  					$(this).dialog('destroy');
	  					$('#dialog').remove();
	  					if ($.isFunction(callback)) callback();
	  					return true;
	  				},
	  				'Cancel': function() {
	  					$(this).dialog('destroy');
	  					$('#dialog').remove();
	  					if ($.isFunction(falseCallBack)) falseCallBack();
	  					return false;
	  				}
	  			}
	  		});
		},
		prompt: function(title, message, default_value,callback, optional_message){
			optional_message = optional_message || "";
			if (title == null || message == null || callback == null)
				return false;
			default_value = default_value || "";
			$('body').append('<div id="dialog" style="display:none;" title="'+title+'"><label for="prompt_value">'+message+'</label>&nbsp;&nbsp;\
						<input type="text" id="prompt_value" value="'+default_value+'"/><br><br><span>'+optional_message+'</span></div>');
			if (optional_message.blank()) optional_message = null;
			$("#dialog").dialog({
	  			bgiframe: true,
	  			resizable: false,
	  			height: optional_message == null ? 300 : 180,
	  			width: optional_message == null ? 300 : 500,
	  			modal: false,
	  			overlay: {
	  				backgroundColor: '#000',
	  				opacity: 0.5
	  			},
	  			closeOnEscape: true,
	  			dialogClass: 'confirm',
	  			close: function(){
	  			  $(this).dialog('destroy');
	  			  $('#dialog').remove();
	  			},
	  			buttons: {
	  				'Ok': function() {
	  				  var value = $('#prompt_value').val();
	  					$(this).dialog('destroy');
	  					$('#dialog').remove();
	  					if ($.isFunction(callback)) callback(value);
	  					return true;
	  				},
	  				'Close': function() {
	  					$(this).dialog('destroy');
	  					$('#dialog').remove();
	  					return false;
	  				}
	  			}
	  		});
		},
		splitAjaxResult: function(data) { //console.log(data, typeof data);
			if (typeof data === "undefined" || data === null) {
				return "操作完成，但返回结果为空";
			}
			var msg, lb_true = "操作成功！", lb_false = "操作失败！！", lb_errno = "\n返回代码: ", lb_error = "\n返回说明: ";
			if (typeof data == "boolean" || typeof data == "string" || typeof data == "number") {
				msg = data ? lb_true : lb_false;
			}
			else if ($.isArray(data) && data.length > 0) {
				msg = data[0] ? lb_true : lb_false;
				if (data.length > 1) {
					msg += lb_errno + data[1];
					if (data.length > 2) msg += lb_error + data[2];
				}
			}
			else if(data && data.success == true || parseInt(data) > 0){
				msg = lb_true;
				if (typeof data.message === "string") {
					msg += "\n返回消息：" + data.message;
				}
			}else{
				msg = lb_false;
				if(typeof data.errors === "object") {
					if(data.errors.code) msg += lb_errno + data.errors.code;
					if(data.errors.reason) msg += lb_error + data.errors.reason;
				}
				else {
					if (data.errno && data.errno > 0) {
						msg += lb_errno + data.errno;
					}
					if (data.error && data.error !== "") {
						msg += lb_error + data.error;
					}
				}
			}
			return msg;
		}
	}, function (){
		log("$$ object extended");
	});


})(Dust, jQuery);


/**
 * 处理ajax操作的返回结果
 * 返回结果的格式
 * {
 *  	success: true or false,
 *  	errors: { code: 'error_code', reason: 'error_reason'},
 * }
 * 
 */
function alertAjaxResult(data, callback)
{
	if(typeof data === "string" && data !== "") data = JSON.parse(data);
	try{
		log(data, typeof data, typeof data.success);
	} catch(e){}
	var msg = '';
	if ($.isArray(data)) {
		$.each(data, function(i, item){
			msg += (i+1) + ": " + Dust.splitAjaxResult(item) + "\n";
		});
	} else {
		msg += Dust.splitAjaxResult(data);
	}
	Dust.alert(msg, '', callback);
}

