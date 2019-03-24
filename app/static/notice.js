function set_notification_count(n) {
            $('#notification_count').text(n);
            $('#notification_count').css('visibility', n ? 'visible' : 'hidden');
        }

        {% if current_user.is_authenticated %}
        $(function() {
        	var since = 0;
        	setInterval(function() {
        		$.ajax('{{ url_for('main.notices') }}?since=' + since).done(
        			function(notices) {
        				for (var i=0; i < notices.lenght; i++) {
        					if (notices[i].name == 'unread_notification_count')
        						set_notification_count(notices[i].data);
        					since = notices[i].timestamp;
        				}
        			}
        		);
        	}, 10000);
        });
        {% endif %}