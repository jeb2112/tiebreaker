---
layout: default
title: Privacy Policy
permalink: /privacy/
---
1. TieBreaker app collects no user data. 
2. It does not access any files on the user's phone, nor write any files to the phone. 
3. That being said, if you go to download the app you will see this dialog:
    ![permissions warning]({{site.baseurl}}/images/tb_warning.png)
4. These permissions are contained in neither the android.manifest.xml, nor in the runtime permission requests in the source code.
5. I do not know where these permissions come from.
6. I opened support ticket number #2-9368000032650 with google-developer-support@google.com, received an answer, but not an answer to this question.
7. I consulted Stack Overflow, and there I found such a hash of dis-, non-, and mis-information about app permissions in the Google Play console that it made my head spin.
8. Whatever these phantom permissions are, they are not actually needed by the app as I wrote it. 
9. I found out that in Android, the user can unilaterally shut down the read and write permissions for this app. From Settings/Apps, drill down on the TieBreaker app to the permissions page. If you see this:

    ![permissions warning 2]({{site.baseurl}}/images/tb_warning_3.png)

    then change it to this:

    ![permissions warning 3]({{site.baseurl}}/images/tb_warning_2.png)

    I recommend all users of this app to do this if they are concerned about data safety and privacy.
10. On behalf of Google, I apologize for the confusion.