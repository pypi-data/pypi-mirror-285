import streamlit.components.v1 as components
import os


def allow_top_navigation(iframe_title):
    """Allow links embedded in iframes to open in the same tab (target='_parent' or '_blank')"""

    components.html('''<script language="javascript">
        var updateAndReloadIframes = function () {
            var reloadRequired = false;
            // Grab all iFrames, add the 'allow-top-navigation' property and reload them
            var iframes = parent.document.querySelectorAll('iframe[title="<<<TITLE>>>"]');
            console.log("allow_top_navigation", iframes.length);
            for (var i = 0; i < iframes.length; i++) {
                if (!iframes[i].sandbox.contains('allow-top-navigation')) {
                    reloadRequired = true;
                    iframes[i].setAttribute("sandbox", "allow-forms allow-modals allow-popups allow-popups-to-escape-sandbox allow-same-origin allow-scripts allow-downloads allow-top-navigation-by-user-activation allow-top-navigation");
                }
            }
            if (reloadRequired) {
                setTimeout(function() {
                    for (var i = 0; i < iframes.length; i++) {
                        iframes[i].contentWindow.location.reload();
                    }
                }, 300)
            }
        }
        updateAndReloadIframes()

    </script>
    '''.replace("<<<TITLE>>>", iframe_title), height=0)
