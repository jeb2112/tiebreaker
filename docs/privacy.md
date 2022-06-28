---
layout: default
title: Privacy Policy
permalink: /privacy/
---
1. TieBreaker app collects no user data. 
2. It does not access any files on the user's phone, nor write any files to the phone. 
3. That being said, the app has READ_EXTERNAL_STORAGE and WRITE_EXTERNAL_STORAGE permissions, according to App Bundle Explorer in Google Play console.
4. These permissions are contained in neither the android.manifest.xml, nor in the runtime permission requests in the source code.
5. I do not know where these permissions come from.
6. I consulted Stack Overflow, and there I found such a hash of dis-, non-, and mis-information about app permissions in the Google Play console that it made my head spin.
6. Whatever these phantom permissions are, they are not actually needed by the app as I wrote it. 
7. I found out that in Android, the user can unilaterally shut down the read and write permissions for this app. I recommend all users of this app to do this if they are concerned about data safety and privacy.
8. On behalf of Google, I apologize for the confusion.