function onElementInserted(containerSelector, elementSelector, callback) {

    var onMutationsObserved = function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.addedNodes.length) {
                var elements = $(mutation.addedNodes).find(elementSelector);
                for (var i = 0, len = elements.length; i < len; i++) {
                    callback(elements[i]);
                }
            }
        });
    };

    var target = $(containerSelector)[0];
    var config = { childList: true, subtree: true };
    var MutationObserver = window.MutationObserver || window.WebKitMutationObserver;
    var observer = new MutationObserver(onMutationsObserved);
    observer.observe(target, config);

}

function on_child_change(mutations) {
  mutations.forEach(function(mutation) {
    var visible_levels = $('#level-log').html();
    $('#log-frame').contents().find("body").children().each(function(index) {
        var level = $(this).attr('class');
        if(visible_levels.indexOf(level) == -1)
            $(this).hide();
        else
            $(this).show()
    });
  });
}


function on_child_load(mutations) {
  mutations.forEach(function(mutation) {
        var target = document.querySelector('#level-log').childNodes[0];
        var obs = new MutationObserver( on_child_change );
        var config = { characterData: false, attributes: false, childList: false, subtree: false, characterData: true};
        obs.observe(target, config);
  });
}

$(document).ready(function() {
    onElementInserted('body', '#log-uid', function(element) {
        var socket = io.connect('http://' + document.domain + ':' + 5000+'/omega_log');
        socket.on('connect', function() {
            var graph = $('#graph-container');
            var text = $('#log-uid').val()+';'+graph.outerWidth()+','+graph.outerHeight();
            socket.emit('connect_event', {data: text});
        });
        socket.on('log_response', function(msg) {
            var str = msg.data;
            var uid = $('#log-uid').val();
            if(str.indexOf(uid)==0)
            {
                message = str.replace(uid,'');
                var iframe = $('#log-frame').contents();
                var iframeBody = iframe.find("body");
                var sub_mes = message.split(': ')[2];
                var level = message.split(': ')[1];
                if(level == 'ERROR')
                {
                    $('#status-area').html('Error: '+sub_mes )
                }
                if(sub_mes == 'start')
                {
                    iframeBody.html('')
                    $('#status-area').html('Backtesting...')
                }
                else if(sub_mes == 'done')
                {
                    $('#status-area').html('Done!')
                }
                else
                {
                    var visible_levels = $('#level-log').html();
                    iframeBody.append('<div class='+level+'>'+message+'</div>');
                    var item = iframeBody.children().last();
                    if(visible_levels.indexOf(level) == -1)
                        item.hide();
                    else
                        item.show();
                }
                iframe.scrollTop(iframe.height());
            }
        });

    });
    onElementInserted('body', '#level-log', function(element) {
        var target = document.querySelector('#level-log');
        var obs = new MutationObserver( on_child_load );
        var config = { characterData: false, attributes: false, childList: true, subtree: false};
        obs.observe(target, config);
    });

});