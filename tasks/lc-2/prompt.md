You are given a 50K-token slice from an OpenClaw gateway error log. Analyze it and:

1. **Identify the top 3 root causes by frequency.** For each, provide:
   - A descriptive name for the error class
   - Approximate count / percentage of total errors
   - 2-3 specific evidence lines (quote them with line numbers)
   - Likely root cause explanation

2. **Severity ranking**: Rank the 3 root causes by operational impact (not just frequency). Justify your ranking.

3. **Remediation**: For each root cause, suggest a specific fix or mitigation.

Be precise. Cite line numbers. Do not hallucinate — only reference errors actually present in the log.

---

**LOG DATA:**

2026-03-07T11:31:53.737Z [telegram] deleteWebhook failed: Network request for 'deleteWebhook' failed!
2026-03-07T11:31:53.755Z [telegram] webhook cleanup failed: Network request for 'deleteWebhook' failed!; retrying in 2.28s.
2026-03-07T11:31:53.758Z [telegram] deleteMyCommands failed: Network request for 'deleteMyCommands' failed!
2026-03-07T11:31:54.240Z [telegram] setMyCommands failed: Network request for 'setMyCommands' failed!
2026-03-07T11:31:54.243Z [telegram] command sync failed: HttpError: Network request for 'setMyCommands' failed!
2026-03-07T11:31:56.579Z [telegram] deleteMyCommands failed: Network request for 'deleteMyCommands' failed!
2026-03-07T11:31:56.586Z [telegram] deleteWebhook failed: Network request for 'deleteWebhook' failed!
2026-03-07T11:31:56.589Z [telegram] webhook cleanup failed: Network request for 'deleteWebhook' failed!; retrying in 4.17s.
2026-03-07T11:31:57.070Z [telegram] setMyCommands failed: Network request for 'setMyCommands' failed!
2026-03-07T11:31:57.073Z [telegram] command sync failed: HttpError: Network request for 'setMyCommands' failed!
2026-03-07T11:32:01.299Z [telegram] deleteWebhook failed: Network request for 'deleteWebhook' failed!
2026-03-07T11:32:01.302Z [telegram] webhook cleanup failed: Network request for 'deleteWebhook' failed!; retrying in 7.15s.
2026-03-07T11:32:01.306Z [telegram] deleteMyCommands failed: Network request for 'deleteMyCommands' failed!
2026-03-07T11:32:01.792Z [telegram] setMyCommands failed: Network request for 'setMyCommands' failed!
2026-03-07T11:32:01.795Z [telegram] command sync failed: HttpError: Network request for 'setMyCommands' failed!
2026-03-07T11:32:08.990Z [telegram] deleteWebhook failed: Network request for 'deleteWebhook' failed!
2026-03-07T11:32:08.992Z [telegram] webhook cleanup failed: Network request for 'deleteWebhook' failed!; retrying in 13.57s.
2026-03-07T11:32:09.125Z [telegram] deleteMyCommands failed: Network request for 'deleteMyCommands' failed!
2026-03-07T11:32:09.607Z [telegram] setMyCommands failed: Network request for 'setMyCommands' failed!
2026-03-07T11:32:09.612Z [telegram] command sync failed: HttpError: Network request for 'setMyCommands' failed!
2026-03-07T11:32:23.109Z [telegram] deleteMyCommands failed: Network request for 'deleteMyCommands' failed!
2026-03-07T11:32:23.140Z [telegram] deleteWebhook failed: Network request for 'deleteWebhook' failed!
2026-03-07T11:32:23.141Z [telegram] webhook cleanup failed: Network request for 'deleteWebhook' failed!; retrying in 21.98s.
2026-03-07T11:32:23.622Z [telegram] setMyCommands failed: Network request for 'setMyCommands' failed!
2026-03-07T11:32:23.625Z [telegram] command sync failed: HttpError: Network request for 'setMyCommands' failed!
2026-03-07T11:32:45.674Z [telegram] deleteMyCommands failed: Network request for 'deleteMyCommands' failed!
2026-03-07T11:32:45.680Z [telegram] deleteWebhook failed: Network request for 'deleteWebhook' failed!
2026-03-07T11:32:45.682Z [telegram] webhook cleanup failed: Network request for 'deleteWebhook' failed!; retrying in 30s.
2026-03-07T11:32:46.163Z [telegram] setMyCommands failed: Network request for 'setMyCommands' failed!
2026-03-07T11:32:46.166Z [telegram] command sync failed: HttpError: Network request for 'setMyCommands' failed!
2026-03-07T11:33:16.230Z [telegram] deleteWebhook failed: Network request for 'deleteWebhook' failed!
2026-03-07T11:33:16.232Z [telegram] webhook cleanup failed: Network request for 'deleteWebhook' failed!; retrying in 30s.
2026-03-07T11:33:16.236Z [telegram] deleteMyCommands failed: Network request for 'deleteMyCommands' failed!
2026-03-07T11:33:16.712Z [telegram] setMyCommands failed: Network request for 'setMyCommands' failed!
2026-03-07T11:33:16.715Z [telegram] command sync failed: HttpError: Network request for 'setMyCommands' failed!
2026-03-07T11:33:46.778Z [telegram] deleteMyCommands failed: Network request for 'deleteMyCommands' failed!
2026-03-07T11:33:46.786Z [telegram] deleteWebhook failed: Network request for 'deleteWebhook' failed!
2026-03-07T11:33:46.788Z [telegram] webhook cleanup failed: Network request for 'deleteWebhook' failed!; retrying in 30s.
2026-03-07T11:33:47.268Z [telegram] setMyCommands failed: Network request for 'setMyCommands' failed!
2026-03-07T11:33:47.270Z [telegram] command sync failed: HttpError: Network request for 'setMyCommands' failed!
2026-03-07T11:34:17.329Z [telegram] deleteMyCommands failed: Network request for 'deleteMyCommands' failed!
2026-03-07T11:34:17.335Z [telegram] deleteWebhook failed: Network request for 'deleteWebhook' failed!
2026-03-07T11:34:17.338Z [telegram] webhook cleanup failed: Network request for 'deleteWebhook' failed!; retrying in 30s.
2026-03-07T11:34:17.814Z [telegram] setMyCommands failed: Network request for 'setMyCommands' failed!
2026-03-07T11:34:17.817Z [telegram] command sync failed: HttpError: Network request for 'setMyCommands' failed!
2026-03-07T11:34:47.884Z [telegram] deleteWebhook failed: Network request for 'deleteWebhook' failed!
2026-03-07T11:34:47.887Z [telegram] webhook cleanup failed: Network request for 'deleteWebhook' failed!; retrying in 30s.
2026-03-07T11:34:47.891Z [telegram] deleteMyCommands failed: Network request for 'deleteMyCommands' failed!
2026-03-07T11:34:48.368Z [telegram] setMyCommands failed: Network request for 'setMyCommands' failed!
2026-03-07T11:34:48.371Z [telegram] command sync failed: HttpError: Network request for 'setMyCommands' failed!
2026-03-07T11:35:18.425Z [telegram] deleteMyCommands failed: Network request for 'deleteMyCommands' failed!
2026-03-07T11:35:18.431Z [telegram] deleteWebhook failed: Network request for 'deleteWebhook' failed!
2026-03-07T11:35:18.433Z [telegram] webhook cleanup failed: Network request for 'deleteWebhook' failed!; retrying in 30s.
2026-03-07T11:35:18.907Z [telegram] setMyCommands failed: Network request for 'setMyCommands' failed!
2026-03-07T11:35:18.910Z [telegram] command sync failed: HttpError: Network request for 'setMyCommands' failed!
2026-03-07T11:35:48.974Z [telegram] deleteMyCommands failed: Network request for 'deleteMyCommands' failed!
2026-03-07T11:35:48.979Z [telegram] deleteWebhook failed: Network request for 'deleteWebhook' failed!
2026-03-07T11:35:48.981Z [telegram] webhook cleanup failed: Network request for 'deleteWebhook' failed!; retrying in 30s.
2026-03-07T11:35:49.458Z [telegram] setMyCommands failed: Network request for 'setMyCommands' failed!
2026-03-07T11:35:49.461Z [telegram] command sync failed: HttpError: Network request for 'setMyCommands' failed!
2026-03-07T11:36:19.530Z [telegram] deleteWebhook failed: Network request for 'deleteWebhook' failed!
2026-03-07T11:36:19.532Z [telegram] webhook cleanup failed: Network request for 'deleteWebhook' failed!; retrying in 30s.
2026-03-07T11:36:19.537Z [telegram] deleteMyCommands failed: Network request for 'deleteMyCommands' failed!
2026-03-07T11:36:20.016Z [telegram] setMyCommands failed: Network request for 'setMyCommands' failed!
2026-03-07T11:36:20.018Z [telegram] command sync failed: HttpError: Network request for 'setMyCommands' failed!
2026-03-07T11:36:50.075Z [telegram] deleteMyCommands failed: Network request for 'deleteMyCommands' failed!
2026-03-07T11:36:50.081Z [telegram] deleteWebhook failed: Network request for 'deleteWebhook' failed!
2026-03-07T11:36:50.083Z [telegram] webhook cleanup failed: Network request for 'deleteWebhook' failed!; retrying in 30s.
2026-03-07T11:36:50.555Z [telegram] setMyCommands failed: Network request for 'setMyCommands' failed!
2026-03-07T11:36:50.558Z [telegram] command sync failed: HttpError: Network request for 'setMyCommands' failed!
2026-03-07T11:37:07.707Z [telegram] deleteWebhook failed: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-07T11:37:07.710Z [telegram] [default] channel exited: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-07T11:37:08.030Z [telegram] deleteMyCommands failed: Call to 'deleteMyCommands' failed! (404: Not Found)
2026-03-07T11:37:08.192Z [telegram] setMyCommands failed: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-07T11:37:08.195Z [telegram] command sync failed: GrammyError: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-07T11:37:13.641Z [telegram] deleteWebhook failed: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-07T11:37:13.644Z [telegram] [default] channel exited: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-07T11:37:13.966Z [telegram] deleteMyCommands failed: Call to 'deleteMyCommands' failed! (404: Not Found)
2026-03-07T11:37:14.126Z [telegram] setMyCommands failed: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-07T11:37:14.128Z [telegram] command sync failed: GrammyError: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-07T11:37:24.681Z [telegram] deleteWebhook failed: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-07T11:37:24.684Z [telegram] [default] channel exited: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-07T11:37:25.005Z [telegram] deleteMyCommands failed: Call to 'deleteMyCommands' failed! (404: Not Found)
2026-03-07T11:37:25.166Z [telegram] setMyCommands failed: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-07T11:37:25.168Z [telegram] command sync failed: GrammyError: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-07T11:37:46.443Z [telegram] deleteWebhook failed: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-07T11:37:46.445Z [telegram] [default] channel exited: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-07T11:37:46.771Z [telegram] deleteMyCommands failed: Call to 'deleteMyCommands' failed! (404: Not Found)
2026-03-07T11:37:46.931Z [telegram] setMyCommands failed: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-07T11:37:46.933Z [telegram] command sync failed: GrammyError: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-07T11:38:29.501Z [telegram] deleteWebhook failed: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-07T11:38:29.504Z [telegram] [default] channel exited: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-07T11:38:29.825Z [telegram] deleteMyCommands failed: Call to 'deleteMyCommands' failed! (404: Not Found)
2026-03-07T11:38:29.983Z [telegram] setMyCommands failed: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-07T11:38:29.985Z [telegram] command sync failed: GrammyError: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-07T11:39:53.183Z [telegram] deleteWebhook failed: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-07T11:39:53.186Z [telegram] [default] channel exited: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-07T11:39:53.191Z [telegram] deleteMyCommands failed: Call to 'deleteMyCommands' failed! (404: Not Found)
2026-03-07T11:39:53.348Z [telegram] setMyCommands failed: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-07T11:39:53.350Z [telegram] command sync failed: GrammyError: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-07T11:42:41.717Z [telegram] deleteWebhook failed: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-07T11:42:41.721Z [telegram] [default] channel exited: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-07T11:42:42.046Z [telegram] deleteMyCommands failed: Call to 'deleteMyCommands' failed! (404: Not Found)
2026-03-07T11:42:42.204Z [telegram] setMyCommands failed: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-07T11:42:42.206Z [telegram] command sync failed: GrammyError: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-07T11:42:47.548Z [telegram] deleteWebhook failed: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-07T11:42:47.550Z [telegram] [default] channel exited: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-07T11:42:47.866Z [telegram] deleteMyCommands failed: Call to 'deleteMyCommands' failed! (404: Not Found)
2026-03-07T11:42:48.025Z [telegram] setMyCommands failed: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-07T11:42:48.027Z [telegram] command sync failed: GrammyError: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-07T11:42:59.204Z [telegram] deleteWebhook failed: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-07T11:42:59.208Z [telegram] [default] channel exited: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-07T11:42:59.536Z [telegram] deleteMyCommands failed: Call to 'deleteMyCommands' failed! (404: Not Found)
2026-03-07T11:42:59.694Z [telegram] setMyCommands failed: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-07T11:42:59.695Z [telegram] command sync failed: GrammyError: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-07T11:43:20.483Z [telegram] deleteWebhook failed: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-07T11:43:20.486Z [telegram] [default] channel exited: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-07T11:43:20.813Z [telegram] deleteMyCommands failed: Call to 'deleteMyCommands' failed! (404: Not Found)
2026-03-07T11:43:20.974Z [telegram] setMyCommands failed: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-07T11:43:20.976Z [telegram] command sync failed: GrammyError: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-07T11:44:04.909Z [telegram] deleteWebhook failed: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-07T11:44:04.910Z [telegram] [default] channel exited: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-07T11:44:05.230Z [telegram] deleteMyCommands failed: Call to 'deleteMyCommands' failed! (404: Not Found)
2026-03-07T11:44:05.389Z [telegram] setMyCommands failed: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-07T11:44:05.391Z [telegram] command sync failed: GrammyError: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-07T11:45:29.740Z [telegram] deleteWebhook failed: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-07T11:45:29.743Z [telegram] [default] channel exited: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-07T11:45:30.068Z [telegram] deleteMyCommands failed: Call to 'deleteMyCommands' failed! (404: Not Found)
2026-03-07T11:45:30.228Z [telegram] setMyCommands failed: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-07T11:45:30.230Z [telegram] command sync failed: GrammyError: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-07T11:46:10.869Z [telegram] deleteWebhook failed: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-07T11:46:10.872Z [telegram] [default] channel exited: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-07T11:46:11.195Z [telegram] deleteMyCommands failed: Call to 'deleteMyCommands' failed! (404: Not Found)
2026-03-07T11:46:11.357Z [telegram] setMyCommands failed: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-07T11:46:11.377Z [telegram] command sync failed: GrammyError: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-07T11:46:11.949Z [bonjour] gateway name conflict resolved; newName="WH-HOME-MINI’s Mac mini (OpenClaw) (2)"
2026-03-07T11:46:11.954Z [bonjour] gateway hostname conflict resolved; newHostname="openclaw-(2)"
2026-03-07T11:46:16.621Z [telegram] deleteWebhook failed: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-07T11:46:16.624Z [telegram] [default] channel exited: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-07T11:46:16.946Z [telegram] deleteMyCommands failed: Call to 'deleteMyCommands' failed! (404: Not Found)
2026-03-07T11:46:17.108Z [telegram] setMyCommands failed: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-07T11:46:17.111Z [telegram] command sync failed: GrammyError: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-07T11:46:27.520Z [telegram] deleteWebhook failed: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-07T11:46:27.523Z [telegram] [default] channel exited: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-07T11:46:27.844Z [telegram] deleteMyCommands failed: Call to 'deleteMyCommands' failed! (404: Not Found)
2026-03-07T11:46:28.006Z [telegram] setMyCommands failed: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-07T11:46:28.009Z [telegram] command sync failed: GrammyError: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-07T11:46:48.830Z [telegram] deleteWebhook failed: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-07T11:46:48.833Z [telegram] [default] channel exited: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-07T11:46:49.158Z [telegram] deleteMyCommands failed: Call to 'deleteMyCommands' failed! (404: Not Found)
2026-03-07T11:46:49.319Z [telegram] setMyCommands failed: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-07T11:46:49.322Z [telegram] command sync failed: GrammyError: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-07T11:47:32.132Z [telegram] deleteWebhook failed: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-07T11:47:32.135Z [telegram] [default] channel exited: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-07T11:47:32.463Z [telegram] deleteMyCommands failed: Call to 'deleteMyCommands' failed! (404: Not Found)
2026-03-07T11:47:32.627Z [telegram] setMyCommands failed: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-07T11:47:32.629Z [telegram] command sync failed: GrammyError: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-07T11:48:57.885Z [telegram] deleteWebhook failed: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-07T11:48:57.888Z [telegram] [default] channel exited: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-07T11:48:58.213Z [telegram] deleteMyCommands failed: Call to 'deleteMyCommands' failed! (404: Not Found)
2026-03-07T11:48:58.375Z [telegram] setMyCommands failed: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-07T11:48:58.377Z [telegram] command sync failed: GrammyError: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-07T11:51:41.291Z [telegram] deleteMyCommands failed: Call to 'deleteMyCommands' failed! (404: Not Found)
2026-03-07T11:51:41.615Z [telegram] deleteWebhook failed: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-07T11:51:41.617Z [telegram] [default] channel exited: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-07T11:51:41.773Z [telegram] setMyCommands failed: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-07T11:51:41.775Z [telegram] command sync failed: GrammyError: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-07T11:51:47.411Z [telegram] deleteWebhook failed: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-07T11:51:47.414Z [telegram] [default] channel exited: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-07T11:51:47.738Z [telegram] deleteMyCommands failed: Call to 'deleteMyCommands' failed! (404: Not Found)
2026-03-07T11:51:47.900Z [telegram] setMyCommands failed: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-07T11:51:47.902Z [telegram] command sync failed: GrammyError: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-07T11:51:58.932Z [telegram] deleteWebhook failed: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-07T11:51:58.935Z [telegram] [default] channel exited: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-07T11:51:59.266Z [telegram] deleteMyCommands failed: Call to 'deleteMyCommands' failed! (404: Not Found)
2026-03-07T11:51:59.427Z [telegram] setMyCommands failed: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-07T11:51:59.429Z [telegram] command sync failed: GrammyError: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-07T11:52:20.682Z [telegram] deleteWebhook failed: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-07T11:52:20.684Z [telegram] [default] channel exited: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-07T11:52:21.007Z [telegram] deleteMyCommands failed: Call to 'deleteMyCommands' failed! (404: Not Found)
2026-03-07T11:52:21.169Z [telegram] setMyCommands failed: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-07T11:52:21.171Z [telegram] command sync failed: GrammyError: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-07T11:53:02.945Z [telegram] deleteWebhook failed: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-07T11:53:02.948Z [telegram] [default] channel exited: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-07T11:53:03.270Z [telegram] deleteMyCommands failed: Call to 'deleteMyCommands' failed! (404: Not Found)
2026-03-07T11:53:03.432Z [telegram] setMyCommands failed: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-07T11:53:03.434Z [telegram] command sync failed: GrammyError: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-07T11:54:25.056Z [telegram] deleteWebhook failed: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-07T11:54:25.059Z [telegram] [default] channel exited: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-07T11:54:25.380Z [telegram] deleteMyCommands failed: Call to 'deleteMyCommands' failed! (404: Not Found)
2026-03-07T11:54:25.541Z [telegram] setMyCommands failed: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-07T11:54:25.543Z [telegram] command sync failed: GrammyError: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-07T03:55:36.047-08:00 Config overwrite: /Users/yourslewis/.openclaw/openclaw.json (sha256 f30d685dcb3c5a3fb279d43cc93c23cd348e589afe3fce11da61394f66e011f1 -> ab6b40d857e5d1051d79934ff72d9b1f54f9edaf5dbf706e29cb1409c71ac19d, backup=/Users/yourslewis/.openclaw/openclaw.json.bak)
2026-03-07T11:55:37.279Z [telegram] deleteWebhook failed: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-07T11:55:37.281Z [telegram] [default] channel exited: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-07T11:55:37.286Z [telegram] deleteMyCommands failed: Call to 'deleteMyCommands' failed! (404: Not Found)
2026-03-07T11:55:37.446Z [telegram] setMyCommands failed: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-07T11:55:37.448Z [telegram] command sync failed: GrammyError: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-07T11:55:43.281Z [telegram] deleteWebhook failed: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-07T11:55:43.283Z [telegram] [default] channel exited: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-07T11:55:43.604Z [telegram] deleteMyCommands failed: Call to 'deleteMyCommands' failed! (404: Not Found)
2026-03-07T11:55:43.766Z [telegram] setMyCommands failed: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-07T11:55:43.768Z [telegram] command sync failed: GrammyError: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-07T11:55:54.712Z [telegram] deleteWebhook failed: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-07T11:55:54.715Z [telegram] [default] channel exited: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-07T11:55:55.042Z [telegram] deleteMyCommands failed: Call to 'deleteMyCommands' failed! (404: Not Found)
2026-03-07T11:55:55.203Z [telegram] setMyCommands failed: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-07T11:55:55.205Z [telegram] command sync failed: GrammyError: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-07T11:56:15.610Z [telegram] deleteWebhook failed: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-07T11:56:15.613Z [telegram] [default] channel exited: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-07T11:56:15.935Z [telegram] deleteMyCommands failed: Call to 'deleteMyCommands' failed! (404: Not Found)
2026-03-07T11:56:16.096Z [telegram] setMyCommands failed: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-07T11:56:16.099Z [telegram] command sync failed: GrammyError: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-07T03:56:56.641-08:00 Config overwrite: /Users/yourslewis/.openclaw/openclaw.json (sha256 ab6b40d857e5d1051d79934ff72d9b1f54f9edaf5dbf706e29cb1409c71ac19d -> 0bc11dc768ab57d0a1ab76030e7c1be3dfa97fa567d3a8087d9104a28c5cd329, backup=/Users/yourslewis/.openclaw/openclaw.json.bak)
2026-03-07T11:56:57.663Z [telegram] deleteWebhook failed: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-07T11:56:57.666Z [telegram] [default] channel exited: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-07T11:56:57.671Z [telegram] deleteMyCommands failed: Call to 'deleteMyCommands' failed! (404: Not Found)
2026-03-07T11:56:57.831Z [telegram] setMyCommands failed: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-07T11:56:57.833Z [telegram] command sync failed: GrammyError: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-07T11:57:03.789Z [telegram] deleteWebhook failed: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-07T11:57:03.792Z [telegram] [default] channel exited: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-07T11:57:04.112Z [telegram] deleteMyCommands failed: Call to 'deleteMyCommands' failed! (404: Not Found)
2026-03-07T11:57:04.272Z [telegram] setMyCommands failed: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-07T11:57:04.275Z [telegram] command sync failed: GrammyError: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-07T11:57:14.611Z [telegram] deleteWebhook failed: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-07T11:57:14.615Z [telegram] [default] channel exited: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-07T11:57:14.936Z [telegram] deleteMyCommands failed: Call to 'deleteMyCommands' failed! (404: Not Found)
2026-03-07T11:57:15.098Z [telegram] setMyCommands failed: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-07T11:57:15.100Z [telegram] command sync failed: GrammyError: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-07T11:57:36.246Z [telegram] deleteWebhook failed: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-07T11:57:36.249Z [telegram] [default] channel exited: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-07T11:57:36.571Z [telegram] deleteMyCommands failed: Call to 'deleteMyCommands' failed! (404: Not Found)
2026-03-07T11:57:36.731Z [telegram] setMyCommands failed: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-07T11:57:36.733Z [telegram] command sync failed: GrammyError: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-07T11:58:08.169Z [telegram] deleteWebhook failed: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-07T11:58:08.173Z [telegram] [default] channel exited: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-07T11:58:08.179Z [telegram] deleteMyCommands failed: Call to 'deleteMyCommands' failed! (404: Not Found)
2026-03-07T11:58:08.342Z [telegram] setMyCommands failed: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-07T11:58:08.363Z [telegram] command sync failed: GrammyError: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-07T11:58:09.395Z [bonjour] gateway name conflict resolved; newName="WH-HOME-MINI’s Mac mini (OpenClaw) (2)"
2026-03-07T11:58:09.396Z [bonjour] gateway hostname conflict resolved; newHostname="openclaw-(2)"
2026-03-07T11:58:14.324Z [telegram] deleteWebhook failed: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-07T11:58:14.327Z [telegram] [default] channel exited: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-07T11:58:14.653Z [telegram] deleteMyCommands failed: Call to 'deleteMyCommands' failed! (404: Not Found)
2026-03-07T11:58:14.816Z [telegram] setMyCommands failed: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-07T11:58:14.819Z [telegram] command sync failed: GrammyError: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-07T11:58:25.478Z [telegram] deleteWebhook failed: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-07T11:58:25.480Z [telegram] [default] channel exited: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-07T11:58:25.804Z [telegram] deleteMyCommands failed: Call to 'deleteMyCommands' failed! (404: Not Found)
2026-03-07T11:58:25.967Z [telegram] setMyCommands failed: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-07T11:58:25.970Z [telegram] command sync failed: GrammyError: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-07T11:58:47.838Z [telegram] deleteWebhook failed: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-07T11:58:47.842Z [telegram] [default] channel exited: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-07T11:58:48.166Z [telegram] deleteMyCommands failed: Call to 'deleteMyCommands' failed! (404: Not Found)
2026-03-07T11:58:48.329Z [telegram] setMyCommands failed: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-07T11:58:48.331Z [telegram] command sync failed: GrammyError: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-07T11:59:28.645Z [telegram] deleteWebhook failed: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-07T11:59:28.647Z [telegram] [default] channel exited: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-07T11:59:28.972Z [telegram] deleteMyCommands failed: Call to 'deleteMyCommands' failed! (404: Not Found)
2026-03-07T11:59:29.133Z [telegram] setMyCommands failed: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-07T11:59:29.135Z [telegram] command sync failed: GrammyError: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-07T12:00:42.758Z [telegram] deleteWebhook failed: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-07T12:00:42.760Z [telegram] [default] channel exited: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-07T12:00:43.082Z [telegram] deleteMyCommands failed: Call to 'deleteMyCommands' failed! (404: Not Found)
2026-03-07T12:00:43.244Z [telegram] setMyCommands failed: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-07T12:00:43.247Z [telegram] command sync failed: GrammyError: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-07T12:00:51.879Z [telegram] deleteWebhook failed: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-07T12:00:51.882Z [telegram] [default] channel exited: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-07T12:00:52.206Z [telegram] deleteMyCommands failed: Call to 'deleteMyCommands' failed! (404: Not Found)
2026-03-07T12:00:52.367Z [telegram] setMyCommands failed: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-07T12:00:52.384Z [telegram] command sync failed: GrammyError: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-07T12:00:53.003Z [bonjour] gateway name conflict resolved; newName="WH-HOME-MINI’s Mac mini (OpenClaw) (2)"
2026-03-07T12:00:53.007Z [bonjour] gateway hostname conflict resolved; newHostname="openclaw-(2)"
2026-03-07T12:00:57.633Z [telegram] deleteWebhook failed: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-07T12:00:57.636Z [telegram] [default] channel exited: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-07T12:00:57.641Z [telegram] deleteMyCommands failed: Call to 'deleteMyCommands' failed! (404: Not Found)
2026-03-07T12:00:57.802Z [telegram] setMyCommands failed: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-07T12:00:57.805Z [telegram] command sync failed: GrammyError: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-07T12:01:08.827Z [telegram] deleteWebhook failed: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-07T12:01:08.831Z [telegram] [default] channel exited: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-07T12:01:09.171Z [telegram] deleteMyCommands failed: Call to 'deleteMyCommands' failed! (404: Not Found)
2026-03-07T12:01:09.334Z [telegram] setMyCommands failed: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-07T12:01:09.337Z [telegram] command sync failed: GrammyError: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-07T12:01:30.942Z [telegram] deleteWebhook failed: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-07T12:01:30.945Z [telegram] [default] channel exited: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-07T12:01:31.269Z [telegram] deleteMyCommands failed: Call to 'deleteMyCommands' failed! (404: Not Found)
2026-03-07T12:01:31.430Z [telegram] setMyCommands failed: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-07T12:01:31.433Z [telegram] command sync failed: GrammyError: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-07T12:02:13.844Z [telegram] deleteWebhook failed: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-07T12:02:13.847Z [telegram] [default] channel exited: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-07T12:02:14.166Z [telegram] deleteMyCommands failed: Call to 'deleteMyCommands' failed! (404: Not Found)
2026-03-07T12:02:14.329Z [telegram] setMyCommands failed: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-07T12:02:14.331Z [telegram] command sync failed: GrammyError: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-07T12:03:38.835Z [telegram] deleteWebhook failed: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-07T12:03:38.838Z [telegram] [default] channel exited: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-07T12:03:39.164Z [telegram] deleteMyCommands failed: Call to 'deleteMyCommands' failed! (404: Not Found)
2026-03-07T12:03:39.328Z [telegram] setMyCommands failed: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-07T12:03:39.330Z [telegram] command sync failed: GrammyError: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-07T04:15:38.026-08:00 Config overwrite: /Users/yourslewis/.openclaw/openclaw.json (sha256 5830763fb492a5d0ea6ab10a2e46708873e36be2710f5cef95a0e2d26e945e38 -> 695785d87dc359113312dc47a17b6e707d0b87b47566f7d45d1a1b1dd2718d72, backup=/Users/yourslewis/.openclaw/openclaw.json.bak)
2026-03-07T12:16:24.848Z [bonjour] gateway name conflict resolved; newName="WH-HOME-MINI’s Mac mini (OpenClaw) (2)"
2026-03-07T12:16:24.854Z [bonjour] gateway hostname conflict resolved; newHostname="openclaw-(2)"
2026-03-07T20:28:38.588Z [telegram] fetch fallback: forcing autoSelectFamily=false + dnsResultOrder=ipv4first
2026-03-08T11:28:13.487Z [telegram] message failed: Call to 'sendMessage' failed! (400: Bad Request: message to be replied not found)
2026-03-08T11:31:02.216Z [telegram] message failed: Call to 'sendMessage' failed! (400: Bad Request: message to be replied not found)
2026-03-08T11:45:46.484Z [telegram] message failed: Call to 'sendMessage' failed! (400: Bad Request: message to be replied not found)
2026-03-08T11:47:01.768Z [telegram] message failed: Call to 'sendMessage' failed! (400: Bad Request: message to be replied not found)
2026-03-08T11:50:33.168Z [reload] config reload skipped (invalid config): : JSON5 parse failed: SyntaxError: JSON5: invalid character '\"' at 14:8
2026-03-08T11:51:24.918Z [reload] config reload skipped (invalid config): : JSON5 parse failed: SyntaxError: JSON5: invalid character '\"' at 14:8
2026-03-08T04:51:45.665-07:00 Failed to read config at /Users/yourslewis/.openclaw/openclaw.json SyntaxError: JSON5: invalid character '\"' at 14:8
    at syntaxError (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:1110:17)
    at invalidChar (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:1055:12)
    at Object.afterPropertyName (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:662:15)
    at Object.default (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:168:37)
    at lex (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:100:42)
    at Object.parse (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:25:17)
    at Object.loadConfig (file:///opt/homebrew/lib/node_modules/openclaw/dist/model-selection-CjMYMtR0.js:10772:111)
    at loadConfig (file:///opt/homebrew/lib/node_modules/openclaw/dist/model-selection-CjMYMtR0.js:11225:20)
    at Object.stopChannel (file:///opt/homebrew/lib/node_modules/openclaw/dist/gateway-cli-vk3t7zJU.js:2490:15)
    at file:///opt/homebrew/lib/node_modules/openclaw/dist/gateway-cli-vk3t7zJU.js:3099:59 {
  lineNumber: 14,
  columnNumber: 8
}
Failed to read config at /Users/yourslewis/.openclaw/openclaw.json SyntaxError: JSON5: invalid character '\"' at 14:8
    at syntaxError (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:1110:17)
    at invalidChar (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:1055:12)
    at Object.afterPropertyName (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:662:15)
    at Object.default (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:168:37)
    at lex (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:100:42)
    at Object.parse (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:25:17)
    at Object.loadConfig (file:///opt/homebrew/lib/node_modules/openclaw/dist/model-selection-CjMYMtR0.js:10772:111)
    at loadConfig (file:///opt/homebrew/lib/node_modules/openclaw/dist/model-selection-CjMYMtR0.js:11225:20)
    at primeConfiguredContextWindows (file:///opt/homebrew/lib/node_modules/openclaw/dist/reply-DhtejUNZ.js:30982:15)
    at ensureContextWindowCacheLoaded (file:///opt/homebrew/lib/node_modules/openclaw/dist/reply-DhtejUNZ.js:31000:14) {
  lineNumber: 14,
  columnNumber: 8
}
Config invalid
File: ~/.openclaw/openclaw.json
Problem:
  - <root>: JSON5 parse failed: SyntaxError: JSON5: invalid character '\"' at 14:8

Run: openclaw doctor --fix
Failed to read config at /Users/yourslewis/.openclaw/openclaw.json SyntaxError: JSON5: invalid character '\"' at 14:8
    at syntaxError (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:1110:17)
    at invalidChar (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:1055:12)
    at Object.afterPropertyName (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:662:15)
    at Object.default (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:168:37)
    at lex (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:100:42)
    at Object.parse (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:25:17)
    at Object.loadConfig (file:///opt/homebrew/lib/node_modules/openclaw/dist/model-selection-CjMYMtR0.js:10772:111)
    at loadConfig (file:///opt/homebrew/lib/node_modules/openclaw/dist/model-selection-CjMYMtR0.js:11225:20)
    at primeConfiguredContextWindows (file:///opt/homebrew/lib/node_modules/openclaw/dist/reply-DhtejUNZ.js:30982:15)
    at ensureContextWindowCacheLoaded (file:///opt/homebrew/lib/node_modules/openclaw/dist/reply-DhtejUNZ.js:31000:14) {
  lineNumber: 14,
  columnNumber: 8
}
Config invalid
File: ~/.openclaw/openclaw.json
Problem:
  - <root>: JSON5 parse failed: SyntaxError: JSON5: invalid character '\"' at 14:8

Run: openclaw doctor --fix
Failed to read config at /Users/yourslewis/.openclaw/openclaw.json SyntaxError: JSON5: invalid character '\"' at 14:8
    at syntaxError (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:1110:17)
    at invalidChar (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:1055:12)
    at Object.afterPropertyName (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:662:15)
    at Object.default (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:168:37)
    at lex (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:100:42)
    at Object.parse (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:25:17)
    at Object.loadConfig (file:///opt/homebrew/lib/node_modules/openclaw/dist/model-selection-CjMYMtR0.js:10772:111)
    at loadConfig (file:///opt/homebrew/lib/node_modules/openclaw/dist/model-selection-CjMYMtR0.js:11225:20)
    at primeConfiguredContextWindows (file:///opt/homebrew/lib/node_modules/openclaw/dist/reply-DhtejUNZ.js:30982:15)
    at ensureContextWindowCacheLoaded (file:///opt/homebrew/lib/node_modules/openclaw/dist/reply-DhtejUNZ.js:31000:14) {
  lineNumber: 14,
  columnNumber: 8
}
Config invalid
File: ~/.openclaw/openclaw.json
Problem:
  - <root>: JSON5 parse failed: SyntaxError: JSON5: invalid character '\"' at 14:8

Run: openclaw doctor --fix
Failed to read config at /Users/yourslewis/.openclaw/openclaw.json SyntaxError: JSON5: invalid character '\"' at 14:8
    at syntaxError (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:1110:17)
    at invalidChar (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:1055:12)
    at Object.afterPropertyName (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:662:15)
    at Object.default (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:168:37)
    at lex (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:100:42)
    at Object.parse (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:25:17)
    at Object.loadConfig (file:///opt/homebrew/lib/node_modules/openclaw/dist/model-selection-CjMYMtR0.js:10772:111)
    at loadConfig (file:///opt/homebrew/lib/node_modules/openclaw/dist/model-selection-CjMYMtR0.js:11225:20)
    at primeConfiguredContextWindows (file:///opt/homebrew/lib/node_modules/openclaw/dist/reply-DhtejUNZ.js:30982:15)
    at ensureContextWindowCacheLoaded (file:///opt/homebrew/lib/node_modules/openclaw/dist/reply-DhtejUNZ.js:31000:14) {
  lineNumber: 14,
  columnNumber: 8
}
Config invalid
File: ~/.openclaw/openclaw.json
Problem:
  - <root>: JSON5 parse failed: SyntaxError: JSON5: invalid character '\"' at 14:8

Run: openclaw doctor --fix
Failed to read config at /Users/yourslewis/.openclaw/openclaw.json SyntaxError: JSON5: invalid character '\"' at 14:8
    at syntaxError (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:1110:17)
    at invalidChar (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:1055:12)
    at Object.afterPropertyName (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:662:15)
    at Object.default (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:168:37)
    at lex (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:100:42)
    at Object.parse (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:25:17)
    at Object.loadConfig (file:///opt/homebrew/lib/node_modules/openclaw/dist/model-selection-CjMYMtR0.js:10772:111)
    at loadConfig (file:///opt/homebrew/lib/node_modules/openclaw/dist/model-selection-CjMYMtR0.js:11225:20)
    at primeConfiguredContextWindows (file:///opt/homebrew/lib/node_modules/openclaw/dist/reply-DhtejUNZ.js:30982:15)
    at ensureContextWindowCacheLoaded (file:///opt/homebrew/lib/node_modules/openclaw/dist/reply-DhtejUNZ.js:31000:14) {
  lineNumber: 14,
  columnNumber: 8
}
Config invalid
File: ~/.openclaw/openclaw.json
Problem:
  - <root>: JSON5 parse failed: SyntaxError: JSON5: invalid character '\"' at 14:8

Run: openclaw doctor --fix
Failed to read config at /Users/yourslewis/.openclaw/openclaw.json SyntaxError: JSON5: invalid character '\"' at 14:8
    at syntaxError (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:1110:17)
    at invalidChar (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:1055:12)
    at Object.afterPropertyName (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:662:15)
    at Object.default (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:168:37)
    at lex (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:100:42)
    at Object.parse (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:25:17)
    at Object.loadConfig (file:///opt/homebrew/lib/node_modules/openclaw/dist/model-selection-CjMYMtR0.js:10772:111)
    at loadConfig (file:///opt/homebrew/lib/node_modules/openclaw/dist/model-selection-CjMYMtR0.js:11225:20)
    at primeConfiguredContextWindows (file:///opt/homebrew/lib/node_modules/openclaw/dist/reply-DhtejUNZ.js:30982:15)
    at ensureContextWindowCacheLoaded (file:///opt/homebrew/lib/node_modules/openclaw/dist/reply-DhtejUNZ.js:31000:14) {
  lineNumber: 14,
  columnNumber: 8
}
Config invalid
File: ~/.openclaw/openclaw.json
Problem:
  - <root>: JSON5 parse failed: SyntaxError: JSON5: invalid character '\"' at 14:8

Run: openclaw doctor --fix
Failed to read config at /Users/yourslewis/.openclaw/openclaw.json SyntaxError: JSON5: invalid character '\"' at 14:8
    at syntaxError (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:1110:17)
    at invalidChar (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:1055:12)
    at Object.afterPropertyName (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:662:15)
    at Object.default (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:168:37)
    at lex (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:100:42)
    at Object.parse (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:25:17)
    at Object.loadConfig (file:///opt/homebrew/lib/node_modules/openclaw/dist/model-selection-CjMYMtR0.js:10772:111)
    at loadConfig (file:///opt/homebrew/lib/node_modules/openclaw/dist/model-selection-CjMYMtR0.js:11225:20)
    at primeConfiguredContextWindows (file:///opt/homebrew/lib/node_modules/openclaw/dist/reply-DhtejUNZ.js:30982:15)
    at ensureContextWindowCacheLoaded (file:///opt/homebrew/lib/node_modules/openclaw/dist/reply-DhtejUNZ.js:31000:14) {
  lineNumber: 14,
  columnNumber: 8
}
Config invalid
File: ~/.openclaw/openclaw.json
Problem:
  - <root>: JSON5 parse failed: SyntaxError: JSON5: invalid character '\"' at 14:8

Run: openclaw doctor --fix
Failed to read config at /Users/yourslewis/.openclaw/openclaw.json SyntaxError: JSON5: invalid character '\"' at 14:8
    at syntaxError (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:1110:17)
    at invalidChar (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:1055:12)
    at Object.afterPropertyName (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:662:15)
    at Object.default (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:168:37)
    at lex (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:100:42)
    at Object.parse (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:25:17)
    at Object.loadConfig (file:///opt/homebrew/lib/node_modules/openclaw/dist/model-selection-CjMYMtR0.js:10772:111)
    at loadConfig (file:///opt/homebrew/lib/node_modules/openclaw/dist/model-selection-CjMYMtR0.js:11225:20)
    at primeConfiguredContextWindows (file:///opt/homebrew/lib/node_modules/openclaw/dist/reply-DhtejUNZ.js:30982:15)
    at ensureContextWindowCacheLoaded (file:///opt/homebrew/lib/node_modules/openclaw/dist/reply-DhtejUNZ.js:31000:14) {
  lineNumber: 14,
  columnNumber: 8
}
Config invalid
File: ~/.openclaw/openclaw.json
Problem:
  - <root>: JSON5 parse failed: SyntaxError: JSON5: invalid character '\"' at 14:8

Run: openclaw doctor --fix
Failed to read config at /Users/yourslewis/.openclaw/openclaw.json SyntaxError: JSON5: invalid character '\"' at 14:8
    at syntaxError (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:1110:17)
    at invalidChar (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:1055:12)
    at Object.afterPropertyName (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:662:15)
    at Object.default (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:168:37)
    at lex (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:100:42)
    at Object.parse (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:25:17)
    at Object.loadConfig (file:///opt/homebrew/lib/node_modules/openclaw/dist/model-selection-CjMYMtR0.js:10772:111)
    at loadConfig (file:///opt/homebrew/lib/node_modules/openclaw/dist/model-selection-CjMYMtR0.js:11225:20)
    at primeConfiguredContextWindows (file:///opt/homebrew/lib/node_modules/openclaw/dist/reply-DhtejUNZ.js:30982:15)
    at ensureContextWindowCacheLoaded (file:///opt/homebrew/lib/node_modules/openclaw/dist/reply-DhtejUNZ.js:31000:14) {
  lineNumber: 14,
  columnNumber: 8
}
Config invalid
File: ~/.openclaw/openclaw.json
Problem:
  - <root>: JSON5 parse failed: SyntaxError: JSON5: invalid character '\"' at 14:8

Run: openclaw doctor --fix
Failed to read config at /Users/yourslewis/.openclaw/openclaw.json SyntaxError: JSON5: invalid character '\"' at 14:8
    at syntaxError (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:1110:17)
    at invalidChar (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:1055:12)
    at Object.afterPropertyName (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:662:15)
    at Object.default (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:168:37)
    at lex (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:100:42)
    at Object.parse (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:25:17)
    at Object.loadConfig (file:///opt/homebrew/lib/node_modules/openclaw/dist/model-selection-CjMYMtR0.js:10772:111)
    at loadConfig (file:///opt/homebrew/lib/node_modules/openclaw/dist/model-selection-CjMYMtR0.js:11225:20)
    at primeConfiguredContextWindows (file:///opt/homebrew/lib/node_modules/openclaw/dist/reply-DhtejUNZ.js:30982:15)
    at ensureContextWindowCacheLoaded (file:///opt/homebrew/lib/node_modules/openclaw/dist/reply-DhtejUNZ.js:31000:14) {
  lineNumber: 14,
  columnNumber: 8
}
Config invalid
File: ~/.openclaw/openclaw.json
Problem:
  - <root>: JSON5 parse failed: SyntaxError: JSON5: invalid character '\"' at 14:8

Run: openclaw doctor --fix
Failed to read config at /Users/yourslewis/.openclaw/openclaw.json SyntaxError: JSON5: invalid character '\"' at 14:8
    at syntaxError (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:1110:17)
    at invalidChar (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:1055:12)
    at Object.afterPropertyName (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:662:15)
    at Object.default (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:168:37)
    at lex (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:100:42)
    at Object.parse (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:25:17)
    at Object.loadConfig (file:///opt/homebrew/lib/node_modules/openclaw/dist/model-selection-CjMYMtR0.js:10772:111)
    at loadConfig (file:///opt/homebrew/lib/node_modules/openclaw/dist/model-selection-CjMYMtR0.js:11225:20)
    at primeConfiguredContextWindows (file:///opt/homebrew/lib/node_modules/openclaw/dist/reply-DhtejUNZ.js:30982:15)
    at ensureContextWindowCacheLoaded (file:///opt/homebrew/lib/node_modules/openclaw/dist/reply-DhtejUNZ.js:31000:14) {
  lineNumber: 14,
  columnNumber: 8
}
Config invalid
File: ~/.openclaw/openclaw.json
Problem:
  - <root>: JSON5 parse failed: SyntaxError: JSON5: invalid character '\"' at 14:8

Run: openclaw doctor --fix
Failed to read config at /Users/yourslewis/.openclaw/openclaw.json SyntaxError: JSON5: invalid character '\"' at 14:8
    at syntaxError (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:1110:17)
    at invalidChar (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:1055:12)
    at Object.afterPropertyName (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:662:15)
    at Object.default (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:168:37)
    at lex (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:100:42)
    at Object.parse (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:25:17)
    at Object.loadConfig (file:///opt/homebrew/lib/node_modules/openclaw/dist/model-selection-CjMYMtR0.js:10772:111)
    at loadConfig (file:///opt/homebrew/lib/node_modules/openclaw/dist/model-selection-CjMYMtR0.js:11225:20)
    at primeConfiguredContextWindows (file:///opt/homebrew/lib/node_modules/openclaw/dist/reply-DhtejUNZ.js:30982:15)
    at ensureContextWindowCacheLoaded (file:///opt/homebrew/lib/node_modules/openclaw/dist/reply-DhtejUNZ.js:31000:14) {
  lineNumber: 14,
  columnNumber: 8
}
Config invalid
File: ~/.openclaw/openclaw.json
Problem:
  - <root>: JSON5 parse failed: SyntaxError: JSON5: invalid character '\"' at 14:8

Run: openclaw doctor --fix
Failed to read config at /Users/yourslewis/.openclaw/openclaw.json SyntaxError: JSON5: invalid character '\"' at 14:8
    at syntaxError (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:1110:17)
    at invalidChar (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:1055:12)
    at Object.afterPropertyName (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:662:15)
    at Object.default (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:168:37)
    at lex (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:100:42)
    at Object.parse (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:25:17)
    at Object.loadConfig (file:///opt/homebrew/lib/node_modules/openclaw/dist/model-selection-CjMYMtR0.js:10772:111)
    at loadConfig (file:///opt/homebrew/lib/node_modules/openclaw/dist/model-selection-CjMYMtR0.js:11225:20)
    at primeConfiguredContextWindows (file:///opt/homebrew/lib/node_modules/openclaw/dist/reply-DhtejUNZ.js:30982:15)
    at ensureContextWindowCacheLoaded (file:///opt/homebrew/lib/node_modules/openclaw/dist/reply-DhtejUNZ.js:31000:14) {
  lineNumber: 14,
  columnNumber: 8
}
Config invalid
File: ~/.openclaw/openclaw.json
Problem:
  - <root>: JSON5 parse failed: SyntaxError: JSON5: invalid character '\"' at 14:8

Run: openclaw doctor --fix
Failed to read config at /Users/yourslewis/.openclaw/openclaw.json SyntaxError: JSON5: invalid character '\"' at 14:8
    at syntaxError (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:1110:17)
    at invalidChar (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:1055:12)
    at Object.afterPropertyName (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:662:15)
    at Object.default (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:168:37)
    at lex (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:100:42)
    at Object.parse (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:25:17)
    at Object.loadConfig (file:///opt/homebrew/lib/node_modules/openclaw/dist/model-selection-CjMYMtR0.js:10772:111)
    at loadConfig (file:///opt/homebrew/lib/node_modules/openclaw/dist/model-selection-CjMYMtR0.js:11225:20)
    at primeConfiguredContextWindows (file:///opt/homebrew/lib/node_modules/openclaw/dist/reply-DhtejUNZ.js:30982:15)
    at ensureContextWindowCacheLoaded (file:///opt/homebrew/lib/node_modules/openclaw/dist/reply-DhtejUNZ.js:31000:14) {
  lineNumber: 14,
  columnNumber: 8
}
Config invalid
File: ~/.openclaw/openclaw.json
Problem:
  - <root>: JSON5 parse failed: SyntaxError: JSON5: invalid character '\"' at 14:8

Run: openclaw doctor --fix
Failed to read config at /Users/yourslewis/.openclaw/openclaw.json SyntaxError: JSON5: invalid character '\"' at 14:8
    at syntaxError (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:1110:17)
    at invalidChar (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:1055:12)
    at Object.afterPropertyName (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:662:15)
    at Object.default (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:168:37)
    at lex (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:100:42)
    at Object.parse (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:25:17)
    at Object.loadConfig (file:///opt/homebrew/lib/node_modules/openclaw/dist/model-selection-CjMYMtR0.js:10772:111)
    at loadConfig (file:///opt/homebrew/lib/node_modules/openclaw/dist/model-selection-CjMYMtR0.js:11225:20)
    at primeConfiguredContextWindows (file:///opt/homebrew/lib/node_modules/openclaw/dist/reply-DhtejUNZ.js:30982:15)
    at ensureContextWindowCacheLoaded (file:///opt/homebrew/lib/node_modules/openclaw/dist/reply-DhtejUNZ.js:31000:14) {
  lineNumber: 14,
  columnNumber: 8
}
Config invalid
File: ~/.openclaw/openclaw.json
Problem:
  - <root>: JSON5 parse failed: SyntaxError: JSON5: invalid character '\"' at 14:8

Run: openclaw doctor --fix
Failed to read config at /Users/yourslewis/.openclaw/openclaw.json SyntaxError: JSON5: invalid character '\"' at 14:8
    at syntaxError (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:1110:17)
    at invalidChar (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:1055:12)
    at Object.afterPropertyName (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:662:15)
    at Object.default (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:168:37)
    at lex (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:100:42)
    at Object.parse (/opt/homebrew/lib/node_modules/openclaw/node_modules/json5/lib/parse.js:25:17)
    at Object.loadConfig (file:///opt/homebrew/lib/node_modules/openclaw/dist/model-selection-CjMYMtR0.js:10772:111)
    at loadConfig (file:///opt/homebrew/lib/node_modules/openclaw/dist/model-selection-CjMYMtR0.js:11225:20)
    at primeConfiguredContextWindows (file:///opt/homebrew/lib/node_modules/openclaw/dist/reply-DhtejUNZ.js:30982:15)
    at ensureContextWindowCacheLoaded (file:///opt/homebrew/lib/node_modules/openclaw/dist/reply-DhtejUNZ.js:31000:14) {
  lineNumber: 14,
  columnNumber: 8
}
Config invalid
File: ~/.openclaw/openclaw.json
Problem:
  - <root>: JSON5 parse failed: SyntaxError: JSON5: invalid character '\"' at 14:8

Run: openclaw doctor --fix
2026-03-08T11:52:18.275Z [telegram] message failed: Call to 'sendMessage' failed! (404: Not Found)
2026-03-08T11:52:18.347Z [delivery-recovery] Retry failed for delivery 1a18c53c-57f4-4659-a888-8b87c3395888: Call to 'sendMessage' failed! (404: Not Found)
2026-03-08T11:52:18.501Z [telegram] deleteMyCommands failed: Call to 'deleteMyCommands' failed! (404: Not Found)
2026-03-08T11:52:18.507Z [telegram] deleteWebhook failed: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-08T11:52:18.509Z [telegram] [default] channel exited: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-08T11:52:18.514Z [telegram] message failed: Call to 'sendMessage' failed! (404: Not Found)
2026-03-08T11:52:18.517Z [delivery-recovery] Retry failed for delivery f41f9a27-6ca1-48b2-8380-0bebc69f8113: Call to 'sendMessage' failed! (404: Not Found)
2026-03-08T11:52:18.676Z [telegram] message failed: Call to 'sendMessage' failed! (404: Not Found)
2026-03-08T11:52:18.681Z [delivery-recovery] Retry failed for delivery 6b91fa9b-0c0d-4dfa-97ca-c1a3263e4eaf: Call to 'sendMessage' failed! (404: Not Found)
2026-03-08T11:52:18.841Z [telegram] message failed: Call to 'sendMessage' failed! (404: Not Found)
2026-03-08T11:52:18.846Z [delivery-recovery] Retry failed for delivery ae9da7ca-2f26-42c8-9f50-af5dcd103c53: Call to 'sendMessage' failed! (404: Not Found)
2026-03-08T11:52:18.981Z [telegram] setMyCommands failed: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-08T11:52:19.000Z [telegram] command sync failed: GrammyError: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-08T11:52:19.654Z [bonjour] gateway name conflict resolved; newName="WH-HOME-MINI’s Mac mini (OpenClaw) (2)"
2026-03-08T11:52:19.660Z [bonjour] gateway hostname conflict resolved; newHostname="openclaw-(2)"
2026-03-08T11:52:24.279Z [telegram] deleteWebhook failed: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-08T11:52:24.283Z [telegram] [default] channel exited: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-08T11:52:24.600Z [telegram] deleteMyCommands failed: Call to 'deleteMyCommands' failed! (404: Not Found)
2026-03-08T11:52:24.759Z [telegram] setMyCommands failed: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-08T11:52:24.761Z [telegram] command sync failed: GrammyError: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-08T11:52:35.259Z [telegram] deleteWebhook failed: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-08T11:52:35.262Z [telegram] [default] channel exited: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-08T11:52:35.566Z [telegram] deleteMyCommands failed: Call to 'deleteMyCommands' failed! (404: Not Found)
2026-03-08T11:52:35.725Z [telegram] setMyCommands failed: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-08T11:52:35.727Z [telegram] command sync failed: GrammyError: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-08T11:52:57.810Z [telegram] deleteWebhook failed: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-08T11:52:57.813Z [telegram] [default] channel exited: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-08T11:52:58.130Z [telegram] deleteMyCommands failed: Call to 'deleteMyCommands' failed! (404: Not Found)
2026-03-08T11:52:58.288Z [telegram] setMyCommands failed: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-08T11:52:58.290Z [telegram] command sync failed: GrammyError: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-08T11:53:15.278Z [telegram] deleteMyCommands failed: Call to 'deleteMyCommands' failed! (404: Not Found)
2026-03-08T11:53:15.285Z [telegram] deleteWebhook failed: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-08T11:53:15.288Z [telegram] [default] channel exited: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-08T11:53:15.768Z [telegram] setMyCommands failed: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-08T11:53:15.790Z [telegram] command sync failed: GrammyError: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-08T11:53:16.475Z [bonjour] gateway name conflict resolved; newName="WH-HOME-MINI’s Mac mini (OpenClaw) (2)"
2026-03-08T11:53:16.475Z [bonjour] gateway hostname conflict resolved; newHostname="openclaw-(2)"
2026-03-08T11:53:21.201Z [telegram] deleteWebhook failed: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-08T11:53:21.203Z [telegram] [default] channel exited: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-08T11:53:21.521Z [telegram] deleteMyCommands failed: Call to 'deleteMyCommands' failed! (404: Not Found)
2026-03-08T11:53:21.681Z [telegram] setMyCommands failed: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-08T11:53:21.684Z [telegram] command sync failed: GrammyError: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-08T11:53:32.771Z [telegram] deleteWebhook failed: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-08T11:53:32.774Z [telegram] [default] channel exited: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-08T11:53:33.098Z [telegram] deleteMyCommands failed: Call to 'deleteMyCommands' failed! (404: Not Found)
2026-03-08T11:53:33.256Z [telegram] setMyCommands failed: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-08T11:53:33.259Z [telegram] command sync failed: GrammyError: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-08T11:53:46.847Z [telegram] deleteWebhook failed: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-08T11:53:46.850Z [telegram] [default] channel exited: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-08T11:53:46.856Z [telegram] deleteMyCommands failed: Call to 'deleteMyCommands' failed! (404: Not Found)
2026-03-08T11:53:47.015Z [telegram] setMyCommands failed: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-08T11:53:47.036Z [telegram] command sync failed: GrammyError: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-08T11:53:47.923Z [bonjour] gateway name conflict resolved; newName="WH-HOME-MINI’s Mac mini (OpenClaw) (2)"
2026-03-08T11:53:47.928Z [bonjour] gateway hostname conflict resolved; newHostname="openclaw-(2)"
2026-03-08T11:53:53.012Z [telegram] deleteWebhook failed: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-08T11:53:53.015Z [telegram] [default] channel exited: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-08T11:53:53.332Z [telegram] deleteMyCommands failed: Call to 'deleteMyCommands' failed! (404: Not Found)
2026-03-08T11:53:53.492Z [telegram] setMyCommands failed: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-08T11:53:53.495Z [telegram] command sync failed: GrammyError: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-08T11:54:04.180Z [telegram] deleteWebhook failed: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-08T11:54:04.183Z [telegram] [default] channel exited: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-08T11:54:04.501Z [telegram] deleteMyCommands failed: Call to 'deleteMyCommands' failed! (404: Not Found)
2026-03-08T11:54:04.659Z [telegram] setMyCommands failed: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-08T11:54:04.661Z [telegram] command sync failed: GrammyError: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-08T11:54:25.167Z [telegram] deleteWebhook failed: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-08T11:54:25.170Z [telegram] [default] channel exited: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-08T11:54:25.494Z [telegram] deleteMyCommands failed: Call to 'deleteMyCommands' failed! (404: Not Found)
2026-03-08T11:54:25.651Z [telegram] setMyCommands failed: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-08T11:54:25.653Z [telegram] command sync failed: GrammyError: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-08T11:54:34.148Z [telegram] message failed: Call to 'sendMessage' failed! (404: Not Found)
2026-03-08T11:54:34.214Z [delivery-recovery] Retry failed for delivery 1a18c53c-57f4-4659-a888-8b87c3395888: Call to 'sendMessage' failed! (404: Not Found)
2026-03-08T11:54:34.367Z [telegram] deleteMyCommands failed: Call to 'deleteMyCommands' failed! (404: Not Found)
2026-03-08T11:54:34.372Z [telegram] deleteWebhook failed: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-08T11:54:34.374Z [telegram] [default] channel exited: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-08T11:54:34.379Z [telegram] message failed: Call to 'sendMessage' failed! (404: Not Found)
2026-03-08T11:54:34.382Z [delivery-recovery] Retry failed for delivery f41f9a27-6ca1-48b2-8380-0bebc69f8113: Call to 'sendMessage' failed! (404: Not Found)
2026-03-08T11:54:34.541Z [telegram] message failed: Call to 'sendMessage' failed! (404: Not Found)
2026-03-08T11:54:34.546Z [delivery-recovery] Retry failed for delivery 6b91fa9b-0c0d-4dfa-97ca-c1a3263e4eaf: Call to 'sendMessage' failed! (404: Not Found)
2026-03-08T11:54:34.705Z [telegram] message failed: Call to 'sendMessage' failed! (404: Not Found)
2026-03-08T11:54:34.711Z [delivery-recovery] Retry failed for delivery ae9da7ca-2f26-42c8-9f50-af5dcd103c53: Call to 'sendMessage' failed! (404: Not Found)
2026-03-08T11:54:34.847Z [telegram] setMyCommands failed: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-08T11:54:34.869Z [telegram] command sync failed: GrammyError: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-08T11:54:35.443Z [bonjour] gateway name conflict resolved; newName="WH-HOME-MINI’s Mac mini (OpenClaw) (2)"
2026-03-08T11:54:35.446Z [bonjour] gateway hostname conflict resolved; newHostname="openclaw-(2)"
2026-03-08T11:54:39.914Z [telegram] deleteWebhook failed: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-08T11:54:39.917Z [telegram] [default] channel exited: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-08T11:54:40.232Z [telegram] deleteMyCommands failed: Call to 'deleteMyCommands' failed! (404: Not Found)
2026-03-08T11:54:40.393Z [telegram] setMyCommands failed: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-08T11:54:40.395Z [telegram] command sync failed: GrammyError: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-08T11:54:50.857Z [telegram] deleteWebhook failed: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-08T11:54:50.859Z [telegram] [default] channel exited: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-08T11:54:51.173Z [telegram] deleteMyCommands failed: Call to 'deleteMyCommands' failed! (404: Not Found)
2026-03-08T11:54:51.332Z [telegram] setMyCommands failed: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-08T11:54:51.334Z [telegram] command sync failed: GrammyError: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-08T11:55:11.676Z [telegram] deleteWebhook failed: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-08T11:55:11.679Z [telegram] [default] channel exited: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-08T11:55:11.997Z [telegram] deleteMyCommands failed: Call to 'deleteMyCommands' failed! (404: Not Found)
2026-03-08T11:55:12.156Z [telegram] setMyCommands failed: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-08T11:55:12.159Z [telegram] command sync failed: GrammyError: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-08T11:55:38.102Z [telegram] message failed: Call to 'sendMessage' failed! (404: Not Found)
2026-03-08T11:55:53.140Z [telegram] deleteWebhook failed: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-08T11:55:53.143Z [telegram] [default] channel exited: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-08T11:55:53.462Z [telegram] deleteMyCommands failed: Call to 'deleteMyCommands' failed! (404: Not Found)
2026-03-08T11:55:53.622Z [telegram] setMyCommands failed: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-08T11:55:53.625Z [telegram] command sync failed: GrammyError: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-08T11:57:19.329Z [telegram] deleteWebhook failed: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-08T11:57:19.332Z [telegram] [default] channel exited: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-08T11:57:19.650Z [telegram] deleteMyCommands failed: Call to 'deleteMyCommands' failed! (404: Not Found)
2026-03-08T11:57:19.813Z [telegram] setMyCommands failed: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-08T11:57:19.815Z [telegram] command sync failed: GrammyError: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-08T11:57:34.112Z [telegram] message failed: Call to 'sendMessage' failed! (404: Not Found)
2026-03-08T11:57:34.290Z [telegram] message failed: Call to 'sendMessage' failed! (404: Not Found)
2026-03-08T12:00:03.720Z [telegram] deleteWebhook failed: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-08T12:00:03.723Z [telegram] [default] channel exited: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-08T12:00:04.039Z [telegram] deleteMyCommands failed: Call to 'deleteMyCommands' failed! (404: Not Found)
2026-03-08T12:00:04.197Z [telegram] setMyCommands failed: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-08T12:00:04.200Z [telegram] command sync failed: GrammyError: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-08T12:00:09.478Z [telegram] deleteWebhook failed: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-08T12:00:09.481Z [telegram] [default] channel exited: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-08T12:00:09.795Z [telegram] deleteMyCommands failed: Call to 'deleteMyCommands' failed! (404: Not Found)
2026-03-08T12:00:09.970Z [telegram] setMyCommands failed: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-08T12:00:09.972Z [telegram] command sync failed: GrammyError: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-08T12:00:20.846Z [telegram] deleteWebhook failed: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-08T12:00:20.849Z [telegram] [default] channel exited: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-08T12:00:21.164Z [telegram] deleteMyCommands failed: Call to 'deleteMyCommands' failed! (404: Not Found)
2026-03-08T12:00:21.327Z [telegram] setMyCommands failed: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-08T12:00:21.330Z [telegram] command sync failed: GrammyError: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-08T12:00:42.520Z [telegram] deleteWebhook failed: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-08T12:00:42.523Z [telegram] [default] channel exited: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-08T12:00:42.850Z [telegram] deleteMyCommands failed: Call to 'deleteMyCommands' failed! (404: Not Found)
2026-03-08T12:00:43.012Z [telegram] setMyCommands failed: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-08T12:00:43.014Z [telegram] command sync failed: GrammyError: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-08T12:01:25.167Z [telegram] deleteWebhook failed: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-08T12:01:25.170Z [telegram] [default] channel exited: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-08T12:01:25.486Z [telegram] deleteMyCommands failed: Call to 'deleteMyCommands' failed! (404: Not Found)
2026-03-08T12:01:25.645Z [telegram] setMyCommands failed: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-08T12:01:25.647Z [telegram] command sync failed: GrammyError: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-08T12:02:49.375Z [telegram] deleteWebhook failed: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-08T12:02:49.378Z [telegram] [default] channel exited: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-08T12:02:49.695Z [telegram] deleteMyCommands failed: Call to 'deleteMyCommands' failed! (404: Not Found)
2026-03-08T12:02:49.855Z [telegram] setMyCommands failed: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-08T12:02:49.858Z [telegram] command sync failed: GrammyError: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-08T12:03:33.056Z [telegram] deleteWebhook failed: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-08T12:03:33.058Z [telegram] [default] channel exited: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-08T12:03:33.375Z [telegram] deleteMyCommands failed: Call to 'deleteMyCommands' failed! (404: Not Found)
2026-03-08T12:03:33.533Z [telegram] setMyCommands failed: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-08T12:03:33.535Z [telegram] command sync failed: GrammyError: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-08T12:03:38.837Z [telegram] deleteWebhook failed: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-08T12:03:38.840Z [telegram] [default] channel exited: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-08T12:03:39.157Z [telegram] deleteMyCommands failed: Call to 'deleteMyCommands' failed! (404: Not Found)
2026-03-08T12:03:39.316Z [telegram] setMyCommands failed: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-08T12:03:39.318Z [telegram] command sync failed: GrammyError: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-08T12:03:49.823Z [telegram] deleteWebhook failed: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-08T12:03:49.826Z [telegram] [default] channel exited: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-08T12:03:50.082Z [telegram] deleteMyCommands failed: Call to 'deleteMyCommands' failed! (404: Not Found)
2026-03-08T12:03:50.242Z [telegram] setMyCommands failed: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-08T12:03:50.244Z [telegram] command sync failed: GrammyError: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-08T12:04:17.075Z [bonjour] gateway name conflict resolved; newName="WH-HOME-MINI’s Mac mini (OpenClaw) (2)"
2026-03-08T12:04:17.081Z [bonjour] gateway hostname conflict resolved; newHostname="openclaw-(2)"
2026-03-08T12:11:53.363Z [telegram] message failed: Call to 'sendMessage' failed! (400: Bad Request: message to be replied not found)
2026-03-09T00:35:29.188-07:00 [telegram] message failed: Call to 'sendMessage' failed! (400: Bad Request: message to be replied not found)
2026-03-09T00:35:29.191-07:00 [delivery-recovery] Retry failed for delivery 1a18c53c-57f4-4659-a888-8b87c3395888: Call to 'sendMessage' failed! (400: Bad Request: message to be replied not found)
2026-03-09T00:35:29.488-07:00 [telegram] message failed: Call to 'sendMessage' failed! (400: Bad Request: message to be replied not found)
2026-03-09T00:35:29.493-07:00 [delivery-recovery] Retry failed for delivery f41f9a27-6ca1-48b2-8380-0bebc69f8113: Call to 'sendMessage' failed! (400: Bad Request: message to be replied not found)
2026-03-09T00:35:29.785-07:00 [telegram] message failed: Call to 'sendMessage' failed! (400: Bad Request: message to be replied not found)
2026-03-09T00:35:29.791-07:00 [delivery-recovery] Retry failed for delivery 6b91fa9b-0c0d-4dfa-97ca-c1a3263e4eaf: Call to 'sendMessage' failed! (400: Bad Request: message to be replied not found)
2026-03-09T00:35:30.076-07:00 [telegram] message failed: Call to 'sendMessage' failed! (400: Bad Request: message to be replied not found)
2026-03-09T00:35:30.082-07:00 [delivery-recovery] Retry failed for delivery ae9da7ca-2f26-42c8-9f50-af5dcd103c53: Call to 'sendMessage' failed! (400: Bad Request: message to be replied not found)
2026-03-09T00:35:30.368-07:00 [telegram] message failed: Call to 'sendMessage' failed! (400: Bad Request: message to be replied not found)
2026-03-09T00:35:30.374-07:00 [delivery-recovery] Retry failed for delivery 3c3afeae-3f28-4fc6-824b-858076183a3e: Call to 'sendMessage' failed! (400: Bad Request: message to be replied not found)
2026-03-09T00:35:30.418-07:00 [bonjour] gateway name conflict resolved; newName="WH-HOME-MINI’s Mac mini (OpenClaw) (2)"
2026-03-09T00:35:30.423-07:00 [bonjour] gateway hostname conflict resolved; newHostname="openclaw-(2)"
2026-03-09T02:12:00.448-07:00 [telegram] Polling stall detected (no getUpdates for 894.31s); forcing restart.
2026-03-09T02:12:00.457-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 2s.
2026-03-09T02:18:02.009-07:00 Config overwrite: /Users/yourslewis/.openclaw/openclaw.json (sha256 628777dfa54a45c08a2cd3ffe1815ba31801bb96ff34068d982689dcbd6add07 -> 6b081cce2d25571daa52b20481e9c49344e740c366cf5e31e50ceb8c4f4caff4, backup=/Users/yourslewis/.openclaw/openclaw.json.bak)
2026-03-09T02:18:10.416-07:00 Config overwrite: /Users/yourslewis/.openclaw/openclaw.json (sha256 6b081cce2d25571daa52b20481e9c49344e740c366cf5e31e50ceb8c4f4caff4 -> 1edab08df565c6313cd206b205bfc375f7543d30628e2f322101a350fe0ccc62, backup=/Users/yourslewis/.openclaw/openclaw.json.bak)
2026-03-09T02:18:22.763-07:00 Config overwrite: /Users/yourslewis/.openclaw/openclaw.json (sha256 1edab08df565c6313cd206b205bfc375f7543d30628e2f322101a350fe0ccc62 -> bd35c1de117add332775745d445504bca03802f8d6f7d36f1fb435855bfcee2d, backup=/Users/yourslewis/.openclaw/openclaw.json.bak)
2026-03-09T02:18:59.440-07:00 Config overwrite: /Users/yourslewis/.openclaw/openclaw.json (sha256 bd35c1de117add332775745d445504bca03802f8d6f7d36f1fb435855bfcee2d -> 2a5c7cc1230b36fcd0d8ab8b58eb5de030913c8c0379285815f6388d98a98a62, backup=/Users/yourslewis/.openclaw/openclaw.json.bak)
2026-03-09T02:19:12.611-07:00 Config overwrite: /Users/yourslewis/.openclaw/openclaw.json (sha256 2a5c7cc1230b36fcd0d8ab8b58eb5de030913c8c0379285815f6388d98a98a62 -> a89181323732e1cd869700e6e7a77733ea9ae95dd2aa1bab301caf5fe4b66ab5, backup=/Users/yourslewis/.openclaw/openclaw.json.bak)
2026-03-09T02:19:53.558-07:00 [telegram] message failed: Call to 'sendMessage' failed! (400: Bad Request: message to be replied not found)
2026-03-09T02:19:53.632-07:00 [delivery-recovery] Retry failed for delivery 1a18c53c-57f4-4659-a888-8b87c3395888: Call to 'sendMessage' failed! (400: Bad Request: message to be replied not found)
2026-03-09T02:19:53.922-07:00 [telegram] message failed: Call to 'sendMessage' failed! (400: Bad Request: message to be replied not found)
2026-03-09T02:19:53.930-07:00 [delivery-recovery] Retry failed for delivery f41f9a27-6ca1-48b2-8380-0bebc69f8113: Call to 'sendMessage' failed! (400: Bad Request: message to be replied not found)
2026-03-09T02:19:54.224-07:00 [telegram] message failed: Call to 'sendMessage' failed! (400: Bad Request: message to be replied not found)
2026-03-09T02:19:54.239-07:00 [delivery-recovery] Retry failed for delivery 6b91fa9b-0c0d-4dfa-97ca-c1a3263e4eaf: Call to 'sendMessage' failed! (400: Bad Request: message to be replied not found)
2026-03-09T02:19:54.585-07:00 [telegram] message failed: Call to 'sendMessage' failed! (400: Bad Request: message to be replied not found)
2026-03-09T02:19:54.591-07:00 [delivery-recovery] Retry failed for delivery ae9da7ca-2f26-42c8-9f50-af5dcd103c53: Call to 'sendMessage' failed! (400: Bad Request: message to be replied not found)
2026-03-09T02:19:54.762-07:00 [bonjour] gateway name conflict resolved; newName="WH-HOME-MINI’s Mac mini (OpenClaw) (2)"
2026-03-09T02:19:54.765-07:00 [bonjour] gateway hostname conflict resolved; newHostname="openclaw-(2)"
2026-03-09T02:19:55.068-07:00 [telegram] message failed: Call to 'sendMessage' failed! (400: Bad Request: message to be replied not found)
2026-03-09T02:19:55.070-07:00 [delivery-recovery] Retry failed for delivery 3c3afeae-3f28-4fc6-824b-858076183a3e: Call to 'sendMessage' failed! (400: Bad Request: message to be replied not found)
2026-03-09T02:32:30.752-07:00 [reload] config reload skipped (invalid config): : JSON5 parse failed: SyntaxError: JSON5: invalid end of input at 260:1
2026-03-09T02:34:30.333-07:00 [delivery-recovery] Delivery 1a18c53c-57f4-4659-a888-8b87c3395888 exceeded max retries (5/5) — moving to failed/
2026-03-09T02:34:30.335-07:00 [delivery-recovery] Delivery f41f9a27-6ca1-48b2-8380-0bebc69f8113 exceeded max retries (5/5) — moving to failed/
2026-03-09T02:34:30.336-07:00 [delivery-recovery] Delivery 6b91fa9b-0c0d-4dfa-97ca-c1a3263e4eaf exceeded max retries (5/5) — moving to failed/
2026-03-09T02:34:30.337-07:00 [delivery-recovery] Delivery ae9da7ca-2f26-42c8-9f50-af5dcd103c53 exceeded max retries (5/5) — moving to failed/
2026-03-09T02:34:30.953-07:00 [telegram] message failed: Call to 'sendMessage' failed! (400: Bad Request: message to be replied not found)
2026-03-09T02:34:31.027-07:00 [delivery-recovery] Retry failed for delivery 3c3afeae-3f28-4fc6-824b-858076183a3e: Call to 'sendMessage' failed! (400: Bad Request: message to be replied not found)
2026-03-09T02:34:32.143-07:00 [bonjour] gateway name conflict resolved; newName="WH-HOME-MINI’s Mac mini (OpenClaw) (2)"
2026-03-09T02:34:32.146-07:00 [bonjour] gateway hostname conflict resolved; newHostname="openclaw-(2)"
2026-03-09T02:48:42.305-07:00 [telegram] Polling stall detected (no getUpdates for 137.48s); forcing restart.
2026-03-09T02:48:42.313-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 2.31s.
2026-03-09T02:58:14.568-07:00 [telegram] Polling stall detected (no getUpdates for 532.03s); forcing restart.
2026-03-09T02:58:14.579-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 4.12s.
2026-03-09T03:14:22.887-07:00 [telegram] Polling stall detected (no getUpdates for 928.28s); forcing restart.
2026-03-09T03:14:22.894-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 7.86s.
2026-03-09T03:31:35.894-07:00 [telegram] Polling stall detected (no getUpdates for 993.43s); forcing restart.
2026-03-09T03:31:35.902-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 12.24s.
2026-03-09T03:42:57.291-07:00 [telegram] Polling stall detected (no getUpdates for 637.66s); forcing restart.
2026-03-09T03:42:57.300-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 24.3s.
2026-03-09T03:58:50.904-07:00 [telegram] Polling stall detected (no getUpdates for 928.22s); forcing restart.
2026-03-09T03:58:50.914-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-09T04:15:43.910-07:00 [telegram] Polling stall detected (no getUpdates for 981.95s); forcing restart.
2026-03-09T04:15:43.917-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-09T04:33:00.917-07:00 [telegram] Polling stall detected (no getUpdates for 1005.95s); forcing restart.
2026-03-09T04:33:00.925-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-09T04:40:56.920-07:00 [telegram] Polling stall detected (no getUpdates for 444.95s); forcing restart.
2026-03-09T04:40:56.926-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-09T04:56:42.929-07:00 [telegram] Polling stall detected (no getUpdates for 914.96s); forcing restart.
2026-03-09T04:56:42.937-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-09T05:01:07.927-07:00 [telegram] Polling stall detected (no getUpdates for 233.95s); forcing restart.
2026-03-09T05:01:07.936-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-09T05:19:04.933-07:00 [telegram] Polling stall detected (no getUpdates for 1045.95s); forcing restart.
2026-03-09T05:19:04.941-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-09T05:37:23.940-07:00 [telegram] Polling stall detected (no getUpdates for 1037.81s); forcing restart.
2026-03-09T05:37:23.949-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-09T05:53:44.946-07:00 [telegram] Polling stall detected (no getUpdates for 949.96s); forcing restart.
2026-03-09T05:53:44.956-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-09T06:00:59.950-07:00 [telegram] Polling stall detected (no getUpdates for 403.96s); forcing restart.
2026-03-09T06:00:59.957-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-09T06:30:04.960-07:00 [telegram] Polling stall detected (no getUpdates for 954.25s); forcing restart.
2026-03-09T06:30:04.968-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-09T06:35:40.476-07:00 [telegram] Polling stall detected (no getUpdates for 218.59s); forcing restart.
2026-03-09T06:35:40.485-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-09T06:51:25.968-07:00 [telegram] Polling stall detected (no getUpdates for 914.44s); forcing restart.
2026-03-09T06:51:25.977-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-09T07:07:28.989-07:00 [telegram] Polling stall detected (no getUpdates for 932s); forcing restart.
2026-03-09T07:07:28.996-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-09T07:23:41.982-07:00 [telegram] Polling stall detected (no getUpdates for 911.77s); forcing restart.
2026-03-09T07:23:41.989-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-09T07:41:20.986-07:00 [telegram] Polling stall detected (no getUpdates for 1027.94s); forcing restart.
2026-03-09T07:41:20.993-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-09T07:48:02.074-07:00 [telegram] Polling stall detected (no getUpdates for 370.03s); forcing restart.
2026-03-09T07:48:02.081-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-09T08:01:59.993-07:00 [telegram] Polling stall detected (no getUpdates for 806.88s); forcing restart.
2026-03-09T08:02:00.001-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-09T08:06:44.831-07:00 [telegram] Polling stall detected (no getUpdates for 253.78s); forcing restart.
2026-03-09T08:06:44.837-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-09T08:11:11.368-07:00 [telegram] Polling stall detected (no getUpdates for 112.36s); forcing restart.
2026-03-09T08:11:11.374-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-09T08:27:19.473-07:00 [telegram] Polling stall detected (no getUpdates for 152.59s); forcing restart.
2026-03-09T08:27:19.478-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-09T08:43:38.010-07:00 [telegram] Polling stall detected (no getUpdates for 947.48s); forcing restart.
2026-03-09T08:43:38.017-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-09T08:52:45.092-07:00 [telegram] Polling stall detected (no getUpdates for 516.01s); forcing restart.
2026-03-09T08:52:45.097-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-09T08:56:04.595-07:00 [telegram] Polling stall detected (no getUpdates for 168.45s); forcing restart.
2026-03-09T08:56:04.603-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-09T09:03:00.015-07:00 [telegram] Polling stall detected (no getUpdates for 384.38s); forcing restart.
2026-03-09T09:03:00.021-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-09T09:13:08.957-07:00 [telegram] Polling stall detected (no getUpdates for 577.89s); forcing restart.
2026-03-09T09:13:08.965-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-09T09:29:17.027-07:00 [telegram] Polling stall detected (no getUpdates for 937.02s); forcing restart.
2026-03-09T09:29:17.036-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-09T09:45:34.032-07:00 [telegram] Polling stall detected (no getUpdates for 915.79s); forcing restart.
2026-03-09T09:45:34.042-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-09T10:03:43.039-07:00 [telegram] Polling stall detected (no getUpdates for 1057.96s); forcing restart.
2026-03-09T10:03:43.048-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-09T10:16:02.167-07:00 [telegram] Polling stall detected (no getUpdates for 708.07s); forcing restart.
2026-03-09T10:16:02.175-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-09T10:32:53.047-07:00 [telegram] Polling stall detected (no getUpdates for 979.82s); forcing restart.
2026-03-09T10:32:53.054-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-09T10:38:32.206-07:00 [telegram] Polling stall detected (no getUpdates for 308.11s); forcing restart.
2026-03-09T10:38:32.212-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-09T10:54:41.058-07:00 [telegram] Polling stall detected (no getUpdates for 937.79s); forcing restart.
2026-03-09T10:54:41.070-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-09T11:04:43.060-07:00 [telegram] Polling stall detected (no getUpdates for 570.95s); forcing restart.
2026-03-09T11:04:43.067-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-09T11:21:20.065-07:00 [telegram] Polling stall detected (no getUpdates for 965.95s); forcing restart.
2026-03-09T11:21:20.071-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-09T11:37:47.071-07:00 [telegram] Polling stall detected (no getUpdates for 925.8s); forcing restart.
2026-03-09T11:37:47.078-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-09T11:53:43.080-07:00 [telegram] Polling stall detected (no getUpdates for 924.96s); forcing restart.
2026-03-09T11:53:43.087-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-09T12:05:44.081-07:00 [telegram] Polling stall detected (no getUpdates for 689.92s); forcing restart.
2026-03-09T12:05:44.090-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-09T12:22:35.087-07:00 [telegram] Polling stall detected (no getUpdates for 979.93s); forcing restart.
2026-03-09T12:22:35.097-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-09T12:39:56.088-07:00 [telegram] Polling stall detected (no getUpdates for 979.79s); forcing restart.
2026-03-09T12:39:56.095-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-09T12:56:12.101-07:00 [telegram] Polling stall detected (no getUpdates for 944.95s); forcing restart.
2026-03-09T12:56:12.109-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-09T13:06:45.101-07:00 [telegram] Polling stall detected (no getUpdates for 601.92s); forcing restart.
2026-03-09T13:06:45.108-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-09T13:14:08.104-07:00 [telegram] Polling stall detected (no getUpdates for 411.94s); forcing restart.
2026-03-09T13:14:08.114-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-09T13:30:54.110-07:00 [telegram] Polling stall detected (no getUpdates for 974.93s); forcing restart.
2026-03-09T13:30:54.118-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-09T13:48:25.117-07:00 [telegram] Polling stall detected (no getUpdates for 989.79s); forcing restart.
2026-03-09T13:48:25.122-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-09T14:05:01.127-07:00 [telegram] Polling stall detected (no getUpdates for 964.95s); forcing restart.
2026-03-09T14:05:01.135-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-09T14:07:45.127-07:00 [telegram] Polling stall detected (no getUpdates for 132.93s); forcing restart.
2026-03-09T14:07:45.133-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-09T14:25:55.131-07:00 [telegram] Polling stall detected (no getUpdates for 1058.95s); forcing restart.
2026-03-09T14:25:55.143-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-09T14:42:31.137-07:00 [telegram] Polling stall detected (no getUpdates for 934.8s); forcing restart.
2026-03-09T14:42:31.146-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-09T14:58:59.143-07:00 [telegram] Polling stall detected (no getUpdates for 956.95s); forcing restart.
2026-03-09T14:58:59.152-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-09T15:08:45.147-07:00 [telegram] Polling stall detected (no getUpdates for 554.96s); forcing restart.
2026-03-09T15:08:45.153-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-09T15:25:53.153-07:00 [telegram] Polling stall detected (no getUpdates for 996.9s); forcing restart.
2026-03-09T15:25:53.160-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-09T15:44:18.159-07:00 [telegram] Polling stall detected (no getUpdates for 1043.79s); forcing restart.
2026-03-09T15:44:18.169-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-09T16:02:14.168-07:00 [telegram] Polling stall detected (no getUpdates for 1044.95s); forcing restart.
2026-03-09T16:02:14.176-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-09T16:09:45.170-07:00 [telegram] Polling stall detected (no getUpdates for 419.94s); forcing restart.
2026-03-09T16:09:45.176-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-09T16:28:43.185-07:00 [telegram] Polling stall detected (no getUpdates for 955.53s); forcing restart.
2026-03-09T16:28:43.198-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-09T16:45:23.182-07:00 [telegram] Polling stall detected (no getUpdates for 968.92s); forcing restart.
2026-03-09T16:45:23.191-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-09T16:58:42.840-07:00 [telegram] Polling stall detected (no getUpdates for 768.6s); forcing restart.
2026-03-09T16:58:42.848-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-09T17:04:28.014-07:00 [telegram] Polling stall detected (no getUpdates for 314.12s); forcing restart.
2026-03-09T17:04:28.023-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-09T17:07:06.276-07:00 [telegram] Polling stall detected (no getUpdates for 127.19s); forcing restart.
2026-03-09T17:07:06.281-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-09T17:10:45.189-07:00 [telegram] Polling stall detected (no getUpdates for 187.85s); forcing restart.
2026-03-09T17:10:45.196-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-09T17:22:13.466-07:00 [telegram] Polling stall detected (no getUpdates for 657.23s); forcing restart.
2026-03-09T17:22:13.477-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-09T17:25:36.652-07:00 [telegram] Polling stall detected (no getUpdates for 172.12s); forcing restart.
2026-03-09T17:25:36.659-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-09T17:28:03.544-07:00 [telegram] Polling stall detected (no getUpdates for 115.88s); forcing restart.
2026-03-09T17:28:03.551-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-09T17:49:31.122-07:00 [telegram] Polling stall detected (no getUpdates for 538.49s); forcing restart.
2026-03-09T17:49:31.132-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-09T18:07:07.210-07:00 [telegram] Polling stall detected (no getUpdates for 1025.04s); forcing restart.
2026-03-09T18:07:07.219-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-09T18:11:45.214-07:00 [telegram] Polling stall detected (no getUpdates for 246.91s); forcing restart.
2026-03-09T18:11:45.224-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-09T18:28:46.218-07:00 [telegram] Polling stall detected (no getUpdates for 989.95s); forcing restart.
2026-03-09T18:28:46.227-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-09T18:46:05.226-07:00 [telegram] Polling stall detected (no getUpdates for 1007.97s); forcing restart.
2026-03-09T18:46:05.235-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-09T19:04:06.230-07:00 [telegram] Polling stall detected (no getUpdates for 1049.96s); forcing restart.
2026-03-09T19:04:06.241-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-09T19:12:45.246-07:00 [telegram] Polling stall detected (no getUpdates for 487.99s); forcing restart.
2026-03-09T19:12:45.253-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-09T19:28:47.255-07:00 [telegram] Polling stall detected (no getUpdates for 930.99s); forcing restart.
2026-03-09T19:28:47.264-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-09T19:45:29.246-07:00 [telegram] Polling stall detected (no getUpdates for 970.89s); forcing restart.
2026-03-09T19:45:29.256-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-09T20:02:13.253-07:00 [telegram] Polling stall detected (no getUpdates for 972.95s); forcing restart.
2026-03-09T20:02:13.264-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-09T20:13:45.259-07:00 [telegram] Polling stall detected (no getUpdates for 660.94s); forcing restart.
2026-03-09T20:13:45.265-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-09T20:29:45.263-07:00 [telegram] Polling stall detected (no getUpdates for 928.95s); forcing restart.
2026-03-09T20:29:45.272-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-09T20:46:53.270-07:00 [telegram] Polling stall detected (no getUpdates for 966.78s); forcing restart.
2026-03-09T20:46:53.276-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-09T21:01:55.593-07:00 [telegram] Polling stall detected (no getUpdates for 871.29s); forcing restart.
2026-03-09T21:01:55.601-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-09T21:14:45.294-07:00 [telegram] Polling stall detected (no getUpdates for 738.67s); forcing restart.
2026-03-09T21:14:45.302-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-09T21:27:08.286-07:00 [telegram] Polling stall detected (no getUpdates for 711.94s); forcing restart.
2026-03-09T21:27:08.292-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-09T21:43:13.933-07:00 [telegram] Polling stall detected (no getUpdates for 934.6s); forcing restart.
2026-03-09T21:43:13.942-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-09T21:56:10.350-07:00 [telegram] Polling stall detected (no getUpdates for 654.58s); forcing restart.
2026-03-09T21:56:10.361-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-09T22:12:25.233-07:00 [telegram] Polling stall detected (no getUpdates for 869.64s); forcing restart.
2026-03-09T22:12:25.239-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-09T22:15:45.302-07:00 [telegram] Polling stall detected (no getUpdates for 169s); forcing restart.
2026-03-09T22:15:45.313-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-09T22:22:59.596-07:00 [telegram] Polling stall detected (no getUpdates for 170.11s); forcing restart.
2026-03-09T22:22:59.602-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-09T22:32:47.779-07:00 [telegram] Polling stall detected (no getUpdates for 557.11s); forcing restart.
2026-03-09T22:32:47.788-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-09T22:45:11.731-07:00 [telegram] Polling stall detected (no getUpdates for 712.86s); forcing restart.
2026-03-09T22:45:11.740-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-09T23:03:38.321-07:00 [telegram] Polling stall detected (no getUpdates for 1075.53s); forcing restart.
2026-03-09T23:03:38.333-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-09T23:20:04.326-07:00 [telegram] Polling stall detected (no getUpdates for 954.96s); forcing restart.
2026-03-09T23:20:04.334-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-09T23:30:21.641-07:00 [telegram] Polling stall detected (no getUpdates for 586.27s); forcing restart.
2026-03-09T23:30:21.650-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-09T23:32:45.661-07:00 [telegram] Polling stall detected (no getUpdates for 112.97s); forcing restart.
2026-03-09T23:32:45.670-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-09T23:47:26.854-07:00 [telegram] Polling stall detected (no getUpdates for 850.14s); forcing restart.
2026-03-09T23:47:26.864-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T00:04:49.343-07:00 [telegram] Polling stall detected (no getUpdates for 1011.44s); forcing restart.
2026-03-10T00:04:49.356-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T00:19:05.349-07:00 [telegram] Polling stall detected (no getUpdates for 824.95s); forcing restart.
2026-03-10T00:19:05.359-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T00:36:37.355-07:00 [telegram] Polling stall detected (no getUpdates for 990.8s); forcing restart.
2026-03-10T00:36:37.366-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T00:54:23.362-07:00 [telegram] Polling stall detected (no getUpdates for 948.28s); forcing restart.
2026-03-10T00:54:23.369-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T01:11:22.368-07:00 [telegram] Polling stall detected (no getUpdates for 987.96s); forcing restart.
2026-03-10T01:11:22.375-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T01:20:05.371-07:00 [telegram] Polling stall detected (no getUpdates for 491.95s); forcing restart.
2026-03-10T01:20:05.381-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T01:38:29.378-07:00 [telegram] Polling stall detected (no getUpdates for 1012.64s); forcing restart.
2026-03-10T01:38:29.385-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T01:55:57.384-07:00 [telegram] Polling stall detected (no getUpdates for 1016.91s); forcing restart.
2026-03-10T01:55:57.392-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T02:13:38.391-07:00 [telegram] Polling stall detected (no getUpdates for 1029.94s); forcing restart.
2026-03-10T02:13:38.396-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T02:30:10.397-07:00 [telegram] Polling stall detected (no getUpdates for 960.96s); forcing restart.
2026-03-10T02:30:10.405-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T02:44:45.672-07:00 [telegram] Polling stall detected (no getUpdates for 814.06s); forcing restart.
2026-03-10T02:44:45.682-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T02:58:12.199-07:00 [telegram] Polling stall detected (no getUpdates for 700.18s); forcing restart.
2026-03-10T02:58:12.209-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T03:14:14.416-07:00 [telegram] Polling stall detected (no getUpdates for 931.15s); forcing restart.
2026-03-10T03:14:14.423-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T03:16:17.016-07:00 [telegram] Polling stall detected (no getUpdates for 91.53s); forcing restart.
2026-03-10T03:16:17.022-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T03:26:34.742-07:00 [telegram] Polling stall detected (no getUpdates for 586.67s); forcing restart.
2026-03-10T03:26:34.750-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T03:42:29.424-07:00 [telegram] Polling stall detected (no getUpdates for 923.63s); forcing restart.
2026-03-10T03:42:29.432-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T03:58:22.430-07:00 [telegram] Polling stall detected (no getUpdates for 921.95s); forcing restart.
2026-03-10T03:58:22.441-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T04:14:22.436-07:00 [telegram] Polling stall detected (no getUpdates for 928.95s); forcing restart.
2026-03-10T04:14:22.443-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T04:32:55.443-07:00 [telegram] Polling stall detected (no getUpdates for 1081.91s); forcing restart.
2026-03-10T04:32:55.453-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T04:51:06.450-07:00 [telegram] Polling stall detected (no getUpdates for 1029.75s); forcing restart.
2026-03-10T04:51:06.460-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T05:07:48.458-07:00 [telegram] Polling stall detected (no getUpdates for 970.92s); forcing restart.
2026-03-10T05:07:48.467-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T05:25:39.462-07:00 [telegram] Polling stall detected (no getUpdates for 1039.93s); forcing restart.
2026-03-10T05:25:39.469-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T05:40:08.468-07:00 [telegram] Polling stall detected (no getUpdates for 837.94s); forcing restart.
2026-03-10T05:40:08.475-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T05:56:52.474-07:00 [telegram] Polling stall detected (no getUpdates for 972.95s); forcing restart.
2026-03-10T05:56:52.484-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T06:00:59.475-07:00 [telegram] Polling stall detected (no getUpdates for 215.94s); forcing restart.
2026-03-10T06:00:59.482-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T06:18:04.482-07:00 [telegram] Polling stall detected (no getUpdates for 993.95s); forcing restart.
2026-03-10T06:18:04.491-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T06:49:19.501-07:00 [telegram] Polling stall detected (no getUpdates for 962.49s); forcing restart.
2026-03-10T06:49:19.507-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T07:06:21.499-07:00 [telegram] Polling stall detected (no getUpdates for 990.93s); forcing restart.
2026-03-10T07:06:21.509-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T07:10:04.877-07:00 [telegram] Polling stall detected (no getUpdates for 131.97s); forcing restart.
2026-03-10T07:10:04.884-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T07:26:05.506-07:00 [telegram] Polling stall detected (no getUpdates for 929.56s); forcing restart.
2026-03-10T07:26:05.516-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T07:42:26.515-07:00 [telegram] Polling stall detected (no getUpdates for 919.79s); forcing restart.
2026-03-10T07:42:26.522-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T07:53:37.206-07:00 [telegram] Polling stall detected (no getUpdates for 639.6s); forcing restart.
2026-03-10T07:53:37.214-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T08:01:59.521-07:00 [telegram] Polling stall detected (no getUpdates for 471.24s); forcing restart.
2026-03-10T08:01:59.528-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T08:04:32.821-07:00 [telegram] Polling stall detected (no getUpdates for 122.23s); forcing restart.
2026-03-10T08:04:32.829-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T08:07:12.349-07:00 [telegram] Polling stall detected (no getUpdates for 128.47s); forcing restart.
2026-03-10T08:07:12.357-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T08:20:15.901-07:00 [telegram] Polling stall detected (no getUpdates for 752.5s); forcing restart.
2026-03-10T08:20:15.910-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T08:23:46.997-07:00 [telegram] Polling stall detected (no getUpdates for 180.01s); forcing restart.
2026-03-10T08:23:47.003-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T08:41:49.534-07:00 [telegram] Polling stall detected (no getUpdates for 1051.48s); forcing restart.
2026-03-10T08:41:49.541-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T08:54:59.846-07:00 [telegram] Polling stall detected (no getUpdates for 759.25s); forcing restart.
2026-03-10T08:54:59.856-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T09:02:59.541-07:00 [telegram] Polling stall detected (no getUpdates for 386.05s); forcing restart.
2026-03-10T09:02:59.550-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T09:20:31.548-07:00 [telegram] Polling stall detected (no getUpdates for 1020.91s); forcing restart.
2026-03-10T09:20:31.557-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T09:37:32.554-07:00 [telegram] Polling stall detected (no getUpdates for 959.64s); forcing restart.
2026-03-10T09:37:32.562-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T09:53:57.563-07:00 [telegram] Polling stall detected (no getUpdates for 953.92s); forcing restart.
2026-03-10T09:53:57.570-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T10:03:59.563-07:00 [telegram] Polling stall detected (no getUpdates for 570.95s); forcing restart.
2026-03-10T10:03:59.570-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T10:19:57.571-07:00 [telegram] Polling stall detected (no getUpdates for 926.93s); forcing restart.
2026-03-10T10:19:57.578-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T10:38:33.576-07:00 [telegram] Polling stall detected (no getUpdates for 1084.94s); forcing restart.
2026-03-10T10:38:33.584-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T10:54:25.584-07:00 [telegram] Polling stall detected (no getUpdates for 920.95s); forcing restart.
2026-03-10T10:54:25.592-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T11:04:59.585-07:00 [telegram] Polling stall detected (no getUpdates for 602.94s); forcing restart.
2026-03-10T11:04:59.593-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T11:21:57.594-07:00 [telegram] Polling stall detected (no getUpdates for 986.95s); forcing restart.
2026-03-10T11:21:57.601-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T11:38:16.597-07:00 [telegram] Polling stall detected (no getUpdates for 947.94s); forcing restart.
2026-03-10T11:38:16.606-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T11:46:40.848-07:00 [telegram] Polling stall detected (no getUpdates for 473.18s); forcing restart.
2026-03-10T11:46:40.857-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T12:02:49.606-07:00 [telegram] Polling stall detected (no getUpdates for 937.7s); forcing restart.
2026-03-10T12:02:49.617-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T12:05:59.607-07:00 [telegram] Polling stall detected (no getUpdates for 158.92s); forcing restart.
2026-03-10T12:05:59.612-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T12:22:18.612-07:00 [telegram] Polling stall detected (no getUpdates for 947.94s); forcing restart.
2026-03-10T12:22:18.619-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T12:39:18.620-07:00 [telegram] Polling stall detected (no getUpdates for 958.8s); forcing restart.
2026-03-10T12:39:18.626-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T12:55:49.625-07:00 [telegram] Polling stall detected (no getUpdates for 959.96s); forcing restart.
2026-03-10T12:55:49.632-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T13:06:59.632-07:00 [telegram] Polling stall detected (no getUpdates for 638.94s); forcing restart.
2026-03-10T13:06:59.640-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T13:23:34.636-07:00 [telegram] Polling stall detected (no getUpdates for 963.92s); forcing restart.
2026-03-10T13:23:34.642-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T13:41:03.644-07:00 [telegram] Polling stall detected (no getUpdates for 987.76s); forcing restart.
2026-03-10T13:41:03.651-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T13:53:08.647-07:00 [telegram] Polling stall detected (no getUpdates for 693.94s); forcing restart.
2026-03-10T13:53:08.654-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T14:07:59.652-07:00 [telegram] Polling stall detected (no getUpdates for 859.95s); forcing restart.
2026-03-10T14:07:59.661-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T14:13:20.844-07:00 [telegram] Polling stall detected (no getUpdates for 290.1s); forcing restart.
2026-03-10T14:13:20.851-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T14:28:59.968-07:00 [telegram] Polling stall detected (no getUpdates for 908.07s); forcing restart.
2026-03-10T14:28:59.976-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T14:34:27.346-07:00 [telegram] Polling stall detected (no getUpdates for 296.31s); forcing restart.
2026-03-10T14:34:27.354-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T14:43:44.567-07:00 [telegram] Polling stall detected (no getUpdates for 526.16s); forcing restart.
2026-03-10T14:43:44.573-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T14:54:13.650-07:00 [telegram] Polling stall detected (no getUpdates for 598.02s); forcing restart.
2026-03-10T14:54:13.657-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T15:08:59.677-07:00 [telegram] Polling stall detected (no getUpdates for 854.97s); forcing restart.
2026-03-10T15:08:59.685-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T15:23:13.786-07:00 [telegram] Polling stall detected (no getUpdates for 823.05s); forcing restart.
2026-03-10T15:23:13.794-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T15:29:27.596-07:00 [telegram] Polling stall detected (no getUpdates for 312.59s); forcing restart.
2026-03-10T15:29:27.604-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T15:39:40.702-07:00 [telegram] Polling stall detected (no getUpdates for 582s); forcing restart.
2026-03-10T15:39:40.709-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T15:48:24.088-07:00 [telegram] Polling stall detected (no getUpdates for 492.33s); forcing restart.
2026-03-10T15:48:24.095-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T16:03:03.389-07:00 [telegram] Polling stall detected (no getUpdates for 848.24s); forcing restart.
2026-03-10T16:03:03.395-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T16:09:59.703-07:00 [telegram] Polling stall detected (no getUpdates for 233.78s); forcing restart.
2026-03-10T16:09:59.712-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T16:27:07.704-07:00 [telegram] Polling stall detected (no getUpdates for 996.92s); forcing restart.
2026-03-10T16:27:07.709-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T16:44:43.711-07:00 [telegram] Polling stall detected (no getUpdates for 1024.95s); forcing restart.
2026-03-10T16:44:43.717-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T16:48:34.036-07:00 [telegram] Polling stall detected (no getUpdates for 199.25s); forcing restart.
2026-03-10T16:48:34.044-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T16:58:57.751-07:00 [telegram] Polling stall detected (no getUpdates for 476.98s); forcing restart.
2026-03-10T16:58:57.759-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T17:10:59.721-07:00 [telegram] Polling stall detected (no getUpdates for 630.55s); forcing restart.
2026-03-10T17:10:59.728-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T17:27:17.728-07:00 [telegram] Polling stall detected (no getUpdates for 946.93s); forcing restart.
2026-03-10T17:27:17.737-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T17:31:46.395-07:00 [telegram] Polling stall detected (no getUpdates for 237.6s); forcing restart.
2026-03-10T17:31:46.403-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T17:49:09.733-07:00 [telegram] Polling stall detected (no getUpdates for 1012.29s); forcing restart.
2026-03-10T17:49:09.743-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T18:06:02.743-07:00 [telegram] Polling stall detected (no getUpdates for 981.95s); forcing restart.
2026-03-10T18:06:02.750-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T18:11:59.741-07:00 [telegram] Polling stall detected (no getUpdates for 325.92s); forcing restart.
2026-03-10T18:11:59.749-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T18:28:22.747-07:00 [telegram] Polling stall detected (no getUpdates for 951.96s); forcing restart.
2026-03-10T18:28:22.754-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T18:32:57.497-07:00 [telegram] Polling stall detected (no getUpdates for 243.69s); forcing restart.
2026-03-10T18:32:57.504-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T18:50:32.755-07:00 [telegram] Polling stall detected (no getUpdates for 956.84s); forcing restart.
2026-03-10T18:50:32.761-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T19:07:47.761-07:00 [telegram] Polling stall detected (no getUpdates for 1003.96s); forcing restart.
2026-03-10T19:07:47.769-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T19:12:59.777-07:00 [telegram] Polling stall detected (no getUpdates for 280.99s); forcing restart.
2026-03-10T19:12:59.784-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T19:30:13.781-07:00 [telegram] Polling stall detected (no getUpdates for 1002.95s); forcing restart.
2026-03-10T19:30:13.786-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T19:46:32.776-07:00 [telegram] Polling stall detected (no getUpdates for 917.78s); forcing restart.
2026-03-10T19:46:32.782-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T20:02:39.780-07:00 [telegram] Polling stall detected (no getUpdates for 935.96s); forcing restart.
2026-03-10T20:02:39.788-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T20:13:59.784-07:00 [telegram] Polling stall detected (no getUpdates for 648.95s); forcing restart.
2026-03-10T20:13:59.791-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T20:31:26.789-07:00 [telegram] Polling stall detected (no getUpdates for 1015.95s); forcing restart.
2026-03-10T20:31:26.795-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T20:48:49.798-07:00 [telegram] Polling stall detected (no getUpdates for 981.8s); forcing restart.
2026-03-10T20:48:49.805-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T21:04:57.803-07:00 [telegram] Polling stall detected (no getUpdates for 936.94s); forcing restart.
2026-03-10T21:04:57.813-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T21:11:47.994-07:00 [telegram] Polling stall detected (no getUpdates for 379.1s); forcing restart.
2026-03-10T21:11:48.001-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T21:14:08.676-07:00 [telegram] Polling stall detected (no getUpdates for 109.62s); forcing restart.
2026-03-10T21:14:08.683-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T21:31:21.811-07:00 [telegram] Polling stall detected (no getUpdates for 1002.08s); forcing restart.
2026-03-10T21:31:21.817-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T21:47:55.816-07:00 [telegram] Polling stall detected (no getUpdates for 932.8s); forcing restart.
2026-03-10T21:47:55.825-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T21:55:53.257-07:00 [telegram] Polling stall detected (no getUpdates for 446.38s); forcing restart.
2026-03-10T21:55:53.263-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T21:58:16.184-07:00 [telegram] Polling stall detected (no getUpdates for 111.85s); forcing restart.
2026-03-10T21:58:16.189-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T22:06:08.822-07:00 [telegram] Polling stall detected (no getUpdates for 441.59s); forcing restart.
2026-03-10T22:06:08.827-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T22:15:08.828-07:00 [telegram] Polling stall detected (no getUpdates for 508.94s); forcing restart.
2026-03-10T22:15:08.832-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T22:32:08.831-07:00 [telegram] Polling stall detected (no getUpdates for 914.46s); forcing restart.
2026-03-10T22:32:08.838-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T22:45:07.985-07:00 [telegram] Polling stall detected (no getUpdates for 571.19s); forcing restart.
2026-03-10T22:45:07.991-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T22:53:08.325-07:00 [telegram] Polling stall detected (no getUpdates for 332.8s); forcing restart.
2026-03-10T22:53:08.331-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T23:08:59.845-07:00 [telegram] Polling stall detected (no getUpdates for 920.48s); forcing restart.
2026-03-10T23:08:59.853-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T23:16:08.848-07:00 [telegram] Polling stall detected (no getUpdates for 397.94s); forcing restart.
2026-03-10T23:16:08.856-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-10T23:30:11.580-07:00 [telegram] Polling stall detected (no getUpdates for 811.7s); forcing restart.
2026-03-10T23:30:11.585-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-11T00:53:43.154-07:00 [telegram] Polling stall detected (no getUpdates for 262.93s); forcing restart.
2026-03-11T00:53:43.161-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-11T01:13:33.893-07:00 [telegram] Polling stall detected (no getUpdates for 1024.66s); forcing restart.
2026-03-11T01:13:33.902-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-11T01:25:10.830-07:00 [telegram] Polling stall detected (no getUpdates for 665.88s); forcing restart.
2026-03-11T01:25:10.837-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-11T01:42:00.905-07:00 [telegram] Polling stall detected (no getUpdates for 979.03s); forcing restart.
2026-03-11T01:42:00.913-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-11T01:54:09.149-07:00 [telegram] Polling stall detected (no getUpdates for 697.19s); forcing restart.
2026-03-11T01:54:09.156-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-11T01:55:32.552-07:00 [tools] browser failed: Error: No supported browser found (Chrome/Brave/Edge/Chromium on macOS, Linux, or Windows).
2026-03-11T02:15:28.264-07:00 [telegram] Polling stall detected (no getUpdates for 565.52s); forcing restart.
2026-03-11T02:15:28.271-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-11T02:20:20.402-07:00 [telegram] Polling stall detected (no getUpdates for 261.09s); forcing restart.
2026-03-11T02:20:20.409-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-11T02:37:14.925-07:00 [telegram] Polling stall detected (no getUpdates for 983.48s); forcing restart.
2026-03-11T02:37:14.935-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-11T02:54:43.883-07:00 [session-write-lock] releasing lock held for 1017388ms (max=720000ms): /Users/yourslewis/.openclaw/agents/main/sessions/6acfaf0a-cb32-45dc-a54b-a58eb813421d.jsonl.lock
2026-03-11T02:54:43.947-07:00 [telegram] Polling stall detected (no getUpdates for 1017.86s); forcing restart.
2026-03-11T02:54:43.952-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-11T02:54:43.964-07:00 [agent/embedded] embedded run timeout: runId=ea657d71-ee64-4c3d-b697-d455d566da25 sessionId=6acfaf0a-cb32-45dc-a54b-a58eb813421d timeoutMs=600000
2026-03-11T02:54:43.993-07:00 [agent/embedded] Profile openai-codex:default timed out. Trying next account...
2026-03-11T03:10:41.938-07:00 [telegram] Polling stall detected (no getUpdates for 914.9s); forcing restart.
2026-03-11T03:10:41.946-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-11T03:28:53.945-07:00 [telegram] Polling stall detected (no getUpdates for 1060.8s); forcing restart.
2026-03-11T03:28:53.954-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-11T03:47:06.952-07:00 [telegram] Polling stall detected (no getUpdates for 1061.98s); forcing restart.
2026-03-11T03:47:06.960-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-11T04:00:54.963-07:00 [telegram] Polling stall detected (no getUpdates for 796.96s); forcing restart.
2026-03-11T04:00:54.970-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-11T04:17:49.964-07:00 [telegram] Polling stall detected (no getUpdates for 983.93s); forcing restart.
2026-03-11T04:17:49.970-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-11T04:34:45.970-07:00 [telegram] Polling stall detected (no getUpdates for 984.96s); forcing restart.
2026-03-11T04:34:45.979-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-11T04:50:52.976-07:00 [telegram] Polling stall detected (no getUpdates for 935.95s); forcing restart.
2026-03-11T04:50:52.983-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-11T05:06:45.981-07:00 [telegram] Polling stall detected (no getUpdates for 921.96s); forcing restart.
2026-03-11T05:06:45.989-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-11T05:13:12.278-07:00 [telegram] Polling stall detected (no getUpdates for 355.25s); forcing restart.
2026-03-11T05:13:12.286-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-11T05:29:02.989-07:00 [telegram] Polling stall detected (no getUpdates for 919.67s); forcing restart.
2026-03-11T05:29:02.997-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-11T05:46:32.995-07:00 [telegram] Polling stall detected (no getUpdates for 988.79s); forcing restart.
2026-03-11T05:46:33.002-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-11T05:50:33.934-07:00 [telegram] Polling stall detected (no getUpdates for 209.87s); forcing restart.
2026-03-11T05:50:33.940-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-11T06:01:00.002-07:00 [telegram] Polling stall detected (no getUpdates for 595.01s); forcing restart.
2026-03-11T06:01:00.011-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-11T06:16:47.009-07:00 [telegram] Polling stall detected (no getUpdates for 915.85s); forcing restart.
2026-03-11T06:16:47.015-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-11T06:19:09.007-07:00 [telegram] Polling stall detected (no getUpdates for 110.91s); forcing restart.
2026-03-11T06:19:09.014-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-11T06:30:09.083-07:00 [telegram] Polling stall detected (no getUpdates for 628.94s); forcing restart.
2026-03-11T06:30:09.091-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-11T07:08:14.031-07:00 [telegram] Polling stall detected (no getUpdates for 976.09s); forcing restart.
2026-03-11T07:08:14.041-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-11T07:24:48.032-07:00 [telegram] Polling stall detected (no getUpdates for 932.74s); forcing restart.
2026-03-11T07:24:48.040-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-11T07:42:15.040-07:00 [telegram] Polling stall detected (no getUpdates for 985.78s); forcing restart.
2026-03-11T07:42:15.048-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-11T07:53:56.762-07:00 [telegram] Polling stall detected (no getUpdates for 670.66s); forcing restart.
2026-03-11T07:53:56.770-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-11T07:58:42.247-07:00 [telegram] Polling stall detected (no getUpdates for 254.42s); forcing restart.
2026-03-11T07:58:42.255-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-11T08:02:01.046-07:00 [telegram] Polling stall detected (no getUpdates for 103.22s); forcing restart.
2026-03-11T08:02:01.054-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-11T08:05:27.648-07:00 [telegram] Polling stall detected (no getUpdates for 175.54s); forcing restart.
2026-03-11T08:05:27.655-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-11T08:19:54.650-07:00 [telegram] Polling stall detected (no getUpdates for 773.39s); forcing restart.
2026-03-11T08:19:54.658-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-11T08:22:48.934-07:00 [telegram] Polling stall detected (no getUpdates for 143.22s); forcing restart.
2026-03-11T08:22:48.938-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-11T08:39:57.059-07:00 [telegram] Polling stall detected (no getUpdates for 997.08s); forcing restart.
2026-03-11T08:39:57.065-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-11T08:54:30.722-07:00 [telegram] Polling stall detected (no getUpdates for 782.31s); forcing restart.
2026-03-11T08:54:30.731-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-11T09:03:01.067-07:00 [telegram] Polling stall detected (no getUpdates for 404.99s); forcing restart.
2026-03-11T09:03:01.074-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-11T09:20:12.074-07:00 [telegram] Polling stall detected (no getUpdates for 999.93s); forcing restart.
2026-03-11T09:20:12.081-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-11T09:36:49.079-07:00 [telegram] Polling stall detected (no getUpdates for 935.8s); forcing restart.
2026-03-11T09:36:49.091-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-11T09:52:58.085-07:00 [telegram] Polling stall detected (no getUpdates for 937.95s); forcing restart.
2026-03-11T09:52:58.095-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-11T10:04:02.089-07:00 [telegram] Polling stall detected (no getUpdates for 632.95s); forcing restart.
2026-03-11T10:04:02.095-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-11T10:12:17.563-07:00 [telegram] Polling stall detected (no getUpdates for 464.4s); forcing restart.
2026-03-11T10:12:17.568-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-11T10:14:59.797-07:00 [telegram] Polling stall detected (no getUpdates for 131.17s); forcing restart.
2026-03-11T10:14:59.801-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-11T10:17:24.327-07:00 [telegram] Polling stall detected (no getUpdates for 113.47s); forcing restart.
2026-03-11T10:17:24.331-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-11T10:21:25.039-07:00 [telegram] Polling stall detected (no getUpdates for 209.64s); forcing restart.
2026-03-11T10:21:25.043-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-11T10:37:11.101-07:00 [telegram] Polling stall detected (no getUpdates for 915.02s); forcing restart.
2026-03-11T10:37:11.108-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-11T10:53:47.107-07:00 [telegram] Polling stall detected (no getUpdates for 964.95s); forcing restart.
2026-03-11T10:53:47.115-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-11T11:05:03.112-07:00 [telegram] Polling stall detected (no getUpdates for 644.96s); forcing restart.
2026-03-11T11:05:03.119-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-11T11:22:06.118-07:00 [telegram] Polling stall detected (no getUpdates for 991.96s); forcing restart.
2026-03-11T11:22:06.127-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-11T11:37:55.124-07:00 [telegram] Polling stall detected (no getUpdates for 917.96s); forcing restart.
2026-03-11T11:37:55.131-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-11T11:54:18.949-07:00 [telegram] Polling stall detected (no getUpdates for 952.77s); forcing restart.
2026-03-11T11:54:18.956-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-11T12:06:03.135-07:00 [telegram] Polling stall detected (no getUpdates for 673.12s); forcing restart.
2026-03-11T12:06:03.146-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-11T12:21:54.143-07:00 [telegram] Polling stall detected (no getUpdates for 919.95s); forcing restart.
2026-03-11T12:21:54.151-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-11T12:32:08.362-07:00 [telegram] Polling stall detected (no getUpdates for 583.15s); forcing restart.
2026-03-11T12:32:08.370-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-11T12:41:50.956-07:00 [telegram] Polling stall detected (no getUpdates for 551.54s); forcing restart.
2026-03-11T12:41:50.964-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-11T13:00:02.154-07:00 [telegram] Polling stall detected (no getUpdates for 1060.16s); forcing restart.
2026-03-11T13:00:02.160-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-11T13:07:03.158-07:00 [telegram] Polling stall detected (no getUpdates for 389.71s); forcing restart.
2026-03-11T13:07:03.166-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-11T13:22:52.162-07:00 [telegram] Polling stall detected (no getUpdates for 916.96s); forcing restart.
2026-03-11T13:22:52.168-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-11T13:39:12.168-07:00 [telegram] Polling stall detected (no getUpdates for 948.94s); forcing restart.
2026-03-11T13:39:12.175-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-11T13:56:43.174-07:00 [telegram] Polling stall detected (no getUpdates for 1019.95s); forcing restart.
2026-03-11T13:56:43.183-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-11T14:08:03.178-07:00 [telegram] Polling stall detected (no getUpdates for 648.95s); forcing restart.
2026-03-11T14:08:03.184-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-11T14:24:10.186-07:00 [telegram] Polling stall detected (no getUpdates for 935.78s); forcing restart.
2026-03-11T14:24:10.194-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-11T14:24:10.198-07:00 [session-write-lock] releasing lock held for 935457ms (max=720000ms): /Users/yourslewis/.openclaw/agents/main/sessions/6acfaf0a-cb32-45dc-a54b-a58eb813421d.jsonl.lock
2026-03-11T14:24:10.218-07:00 [agent/embedded] embedded run timeout: runId=4a385912-93bd-4c39-b96b-5ea4c7b134bb sessionId=6acfaf0a-cb32-45dc-a54b-a58eb813421d timeoutMs=600000
2026-03-11T14:24:10.238-07:00 [agent/embedded] Profile openai-codex:default timed out. Trying next account...
2026-03-11T14:32:08.189-07:00 [telegram] Polling stall detected (no getUpdates for 416.63s); forcing restart.
2026-03-11T14:32:08.198-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-11T14:50:12.194-07:00 [telegram] Polling stall detected (no getUpdates for 1052.8s); forcing restart.
2026-03-11T14:50:12.201-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-11T15:06:02.200-07:00 [telegram] Polling stall detected (no getUpdates for 918.79s); forcing restart.
2026-03-11T15:06:02.207-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-11T15:06:02.211-07:00 [session-write-lock] releasing lock held for 917492ms (max=720000ms): /Users/yourslewis/.openclaw/agents/main/sessions/6acfaf0a-cb32-45dc-a54b-a58eb813421d.jsonl.lock
2026-03-11T15:06:02.221-07:00 [agent/embedded] embedded run timeout: runId=ee80c619-361e-4aec-83fd-1910a0ccff3b sessionId=6acfaf0a-cb32-45dc-a54b-a58eb813421d timeoutMs=600000
2026-03-11T15:06:02.233-07:00 [agent/embedded] Profile openai-codex:default timed out. Trying next account...
2026-03-11T15:06:44.056-07:00 [gateway] full process restart failed (Bootstrap failed: 5: Input/output error Try re-running the command as root for richer errors.); falling back to in-process restart
2026-03-11T15:06:44.723-07:00 [telegram] message failed: Call to 'sendMessage' failed! (400: Bad Request: message to be replied not found)
2026-03-11T15:06:44.732-07:00 [delivery-recovery] Retry failed for delivery 3c3afeae-3f28-4fc6-824b-858076183a3e: Call to 'sendMessage' failed! (400: Bad Request: message to be replied not found)
2026-03-11T15:06:46.187-07:00 [bonjour] gateway name conflict resolved; newName="WH-HOME-MINI’s Mac mini (OpenClaw) (2)"
2026-03-11T15:06:46.193-07:00 [bonjour] gateway hostname conflict resolved; newHostname="openclaw-(2)"
2026-03-11T15:09:05.690-07:00 [delivery-recovery] Delivery 3c3afeae-3f28-4fc6-824b-858076183a3e exceeded max retries (5/5) — moving to failed/
2026-03-11T15:25:47.229-07:00 [telegram] Polling stall detected (no getUpdates for 962.94s); forcing restart.
2026-03-11T15:25:47.238-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 2.32s.
2026-03-11T15:26:05.351-07:00 [bonjour] gateway name conflict resolved; newName="WH-HOME-MINI’s Mac mini (OpenClaw) (3)"
2026-03-11T15:26:05.360-07:00 [bonjour] gateway hostname conflict resolved; newHostname="openclaw-(3)"
2026-03-11T15:42:09.213-07:00 [telegram] Polling stall detected (no getUpdates for 942.08s); forcing restart.
2026-03-11T15:42:09.224-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 3.84s.
2026-03-11T15:42:31.717-07:00 [tools] read failed: ENOENT: no such file or directory, access '/Users/yourslewis/.openclaw/workspace/memory/2026-03-11.md'
2026-03-11T15:42:31.727-07:00 [tools] read failed: ENOENT: no such file or directory, access '/Users/yourslewis/.openclaw/workspace/memory/2026-03-10.md'
2026-03-11T15:42:31.733-07:00 [tools] read failed: ENOENT: no such file or directory, access '/Users/yourslewis/.openclaw/workspace/MEMORY.md'
2026-03-11T15:58:56.220-07:00 [telegram] Polling stall detected (no getUpdates for 966.71s); forcing restart.
2026-03-11T15:58:56.229-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 6.48s.
2026-03-11T16:10:03.224-07:00 [telegram] Polling stall detected (no getUpdates for 628.57s); forcing restart.
2026-03-11T16:10:03.231-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 13.88s.
2026-03-11T16:37:18.241-07:00 [telegram] Polling stall detected (no getUpdates for 949.99s); forcing restart.
2026-03-11T16:37:18.249-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 22.19s.
2026-03-11T16:42:43.433-07:00 [telegram] Polling stall detected (no getUpdates for 301.91s); forcing restart.
2026-03-11T16:42:43.441-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-11T16:45:42.974-07:00 [telegram] Polling stall detected (no getUpdates for 148.48s); forcing restart.
2026-03-11T16:45:42.983-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-11T16:48:07.118-07:00 [telegram] Polling stall detected (no getUpdates for 113.13s); forcing restart.
2026-03-11T16:48:07.125-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-11T16:59:05.114-07:00 [telegram] Polling stall detected (no getUpdates for 236.4s); forcing restart.
2026-03-11T16:59:05.120-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-11T17:08:28.583-07:00 [telegram] Polling stall detected (no getUpdates for 532.38s); forcing restart.
2026-03-11T17:08:28.593-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-11T17:11:03.245-07:00 [telegram] Polling stall detected (no getUpdates for 123.59s); forcing restart.
2026-03-11T17:11:03.254-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-11T17:27:33.252-07:00 [telegram] Polling stall detected (no getUpdates for 958.96s); forcing restart.
2026-03-11T17:27:33.263-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-11T17:39:39.903-07:00 [telegram] Polling stall detected (no getUpdates for 695.6s); forcing restart.
2026-03-11T17:39:39.914-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 30s.
2026-03-11T18:59:55.679-07:00 [agent/embedded] embedded run agent end: runId=20faa843-b0ba-4fc1-b9f9-15fa0c7b3382 isError=true error=Codex error: {"type":"error","error":{"type":"server_error","code":"server_error","message":"An error occurred while processing your request. You can retry your request, or contact us through our help center at help.openai.com if the error persists. Please include the request ID 9a3473a6-cee0-4b89-8f5a-59e5a47afe7f in your message.","param":null},"sequence_number":2}
2026-03-11T19:10:06.316-07:00 [agent/embedded] embedded run agent end: runId=8e00fa6c-d233-4d37-aea1-191b99d9e0bb isError=true error=Codex error: {"type":"error","error":{"type":"server_error","code":"server_error","message":"An error occurred while processing your request. You can retry your request, or contact us through our help center at help.openai.com if the error persists. Please include the request ID 2d81b8dd-5579-4ef6-afd3-6210129fe053 in your message.","param":null},"sequence_number":2}
2026-03-11T19:12:07.122-07:00 [agent/embedded] embedded run agent end: runId=6583250f-01a9-4d39-8f0d-2ebbac0c5e10 isError=true error=⚠️ API rate limit reached. Please try again later.
2026-03-11T19:12:15.249-07:00 [agent/embedded] embedded run agent end: runId=6583250f-01a9-4d39-8f0d-2ebbac0c5e10 isError=true error=⚠️ API rate limit reached. Please try again later.
2026-03-11T23:59:22.515-07:00 [agent/embedded] embedded run timeout: runId=ab9b0f4d-45a0-40e9-8f66-c1ecaac19671 sessionId=c7d4500b-1aa7-4478-a7dd-0fdc5d9284e6 timeoutMs=600000
2026-03-11T23:59:22.521-07:00 [agent/embedded] Profile openai-codex:default timed out. Trying next account...
2026-03-12T08:26:06.386-07:00 [tools] exec failed: zsh:1: command not found: python

Command not found
2026-03-12T19:28:48.729-07:00 [tools] read failed: ENOENT: no such file or directory, access '/Users/yourslewis/.openclaw/workspace/kaggle/playground-series-s6e3/outputs/raw_plus_target_encoding_models_report.json'
2026-03-13T20:02:54.738-07:00 [agent/embedded] embedded run agent end: runId=b27a0a45-d13b-4f3c-84b5-24c71647ea7a isError=true error=⚠️ API rate limit reached. Please try again later.
2026-03-13T20:03:19.825-07:00 [agent/embedded] embedded run agent end: runId=03f95cae-ea59-4a9d-beed-dd893aa6cd91 isError=true error=⚠️ API rate limit reached. Please try again later.
2026-03-13T20:03:57.463-07:00 [agent/embedded] embedded run agent end: runId=bc25bf48-ba5f-40a7-9c9f-eb93f55d6726 isError=true error=⚠️ API rate limit reached. Please try again later.
2026-03-13T20:05:41.683-07:00 [compaction] Full summarization failed, trying partial: Summarization failed: You have hit your ChatGPT usage limit (plus plan). Try again in ~6597 min.
2026-03-13T20:06:08.119-07:00 [compaction] Partial summarization also failed: Summarization failed: You have hit your ChatGPT usage limit (plus plan). Try again in ~6597 min.
2026-03-13T20:06:35.243-07:00 [compaction] Full summarization failed, trying partial: Summarization failed: You have hit your ChatGPT usage limit (plus plan). Try again in ~6596 min.
2026-03-13T20:07:01.833-07:00 [compaction] Partial summarization also failed: Summarization failed: You have hit your ChatGPT usage limit (plus plan). Try again in ~6596 min.
2026-03-13T20:07:28.574-07:00 [compaction] Full summarization failed, trying partial: Summarization failed: You have hit your ChatGPT usage limit (plus plan). Try again in ~6596 min.
2026-03-13T20:07:55.400-07:00 [compaction] Partial summarization also failed: Summarization failed: You have hit your ChatGPT usage limit (plus plan). Try again in ~6595 min.
2026-03-13T20:08:21.856-07:00 [compaction] Full summarization failed, trying partial: Summarization failed: You have hit your ChatGPT usage limit (plus plan). Try again in ~6595 min.
2026-03-13T20:08:48.928-07:00 [compaction] Partial summarization also failed: Summarization failed: You have hit your ChatGPT usage limit (plus plan). Try again in ~6594 min.
2026-03-13T20:09:15.340-07:00 [agent/embedded] embedded run agent end: runId=eeae0aa3-3075-44e6-9e69-837d1ef89e4f isError=true error=⚠️ API rate limit reached. Please try again later.
2026-03-13T20:14:23.998-07:00 [agent/embedded] embedded run agent end: runId=a61d95f7-5c0b-4f5c-b308-6d607588dbe4 isError=true error=⚠️ API rate limit reached. Please try again later.
2026-03-13T20:14:24.298-07:00 [telegram] sendMessage failed: Call to 'sendMessage' failed! (400: Bad Request: message to be replied not found)
2026-03-13T20:14:24.299-07:00 [telegram] final reply failed: GrammyError: Call to 'sendMessage' failed! (400: Bad Request: message to be replied not found)
2026-03-13T20:14:56.544-07:00 [agent/embedded] embedded run agent end: runId=15239605-26fb-48a2-ae1c-eedfe0f4264b isError=true error=⚠️ API rate limit reached. Please try again later.
2026-03-13T20:15:18.891-07:00 [agent/embedded] embedded run agent end: runId=7e297647-831f-4e8c-9ef7-e363cc07da6a isError=true error=⚠️ API rate limit reached. Please try again later.
2026-03-13T20:18:03.722-07:00 [agent/embedded] embedded run agent end: runId=a7884216-2365-4cfa-8a6f-8784d8e01456 isError=true error=⚠️ API rate limit reached. Please try again later.
2026-03-13T20:18:04.391-07:00 [telegram] sendMessage failed: Call to 'sendMessage' failed! (400: Bad Request: message to be replied not found)
2026-03-13T20:18:04.392-07:00 [telegram] final reply failed: GrammyError: Call to 'sendMessage' failed! (400: Bad Request: message to be replied not found)
2026-03-13T20:44:27.710-07:00 [agent/embedded] embedded run agent end: runId=4dec6cec-1862-45c1-8539-1a718fc7c382 isError=true error=⚠️ API rate limit reached. Please try again later.
2026-03-13T21:28:52.057-07:00 [tools] read failed: ENOENT: no such file or directory, access '/Users/yourslewis/.openclaw/workspace/MEMORY.md'
2026-03-13T21:28:52.062-07:00 [tools] read failed: ENOENT: no such file or directory, access '/Users/yourslewis/.openclaw/workspace/memory/2026-03-14.md'
2026-03-13T21:28:52.066-07:00 [tools] read failed: ENOENT: no such file or directory, access '/Users/yourslewis/.openclaw/workspace/memory/2026-03-13.md'
2026-03-14T02:02:32.949-07:00 [tools] read failed: ENOENT: no such file or directory, access '/Users/yourslewis/.openclaw/workspace/kaggle/playground-series-s6e3/outputs/catboost_group_all_tuning_report.json'
2026-03-15T06:25:29.374-07:00 [tools] read failed: ENOENT: no such file or directory, access '/Users/yourslewis/.openclaw/workspace/memory/2026-03-15.md'
2026-03-15T06:25:29.384-07:00 [tools] read failed: ENOENT: no such file or directory, access '/Users/yourslewis/.openclaw/workspace/memory/2026-03-14.md'
2026-03-15T06:25:29.390-07:00 [tools] read failed: ENOENT: no such file or directory, access '/Users/yourslewis/.openclaw/workspace/MEMORY.md'
2026-03-15T13:48:36.261-07:00 [tools] read failed: ENOENT: no such file or directory, access '/Users/yourslewis/.openclaw/workspace/memory/2026-03-15.md'
2026-03-15T13:49:02.809-07:00 [agent/embedded] embedded run agent end: runId=46875208-5629-4061-90f9-cb488ec23f9a isError=true error=Unknown error
2026-03-15T15:49:44.466-07:00 [tools] read failed: ENOENT: no such file or directory, access '/Users/yourslewis/.openclaw/workspace/memory/2026-03-14.md'
2026-03-15T15:49:44.470-07:00 [tools] read failed: ENOENT: no such file or directory, access '/Users/yourslewis/.openclaw/workspace/MEMORY.md'
2026-03-15T15:50:05.786-07:00 [telegram] answerCallbackQuery failed: Call to 'answerCallbackQuery' failed! (400: Bad Request: query is too old and response timeout expired or query ID is invalid)
2026-03-15T21:44:35.937-07:00 [agent/embedded] embedded run agent end: runId=34f66123-b531-4566-8220-5ebed9e83b21 isError=true error=Unknown error
2026-03-15T21:50:57.065-07:00 [compaction] Full summarization failed, trying partial: Summarization failed: Unknown error
2026-03-15T21:51:00.525-07:00 [compaction] Partial summarization also failed: Summarization failed: Unknown error
2026-03-15T21:51:04.191-07:00 [compaction] Full summarization failed, trying partial: Summarization failed: Unknown error
2026-03-15T21:51:07.582-07:00 [compaction] Partial summarization also failed: Summarization failed: Unknown error
2026-03-15T22:17:53.018-07:00 [agent/embedded] embedded run agent end: runId=8649f1ec-6afd-4d03-84b1-5185bd8c2dc3 isError=true error=Unknown error
2026-03-15T22:17:54.215-07:00 [agent/embedded] embedded run agent end: runId=3534fe85-b4e0-4dc8-9ff0-9b76dbc8ca03 isError=true error=Unknown error
2026-03-15T22:20:21.918-07:00 [agent/embedded] embedded run agent end: runId=e8bb310c-8c93-4719-bf7f-0d8706e0ea2d isError=true error=Unknown error
2026-03-15T22:20:45.739-07:00 [agent/embedded] embedded run agent end: runId=37505fb8-ef7b-457c-80ae-5292d96ac418 isError=true error=Unknown error
2026-03-15T22:21:31.654-07:00 [tools] read failed: ENOENT: no such file or directory, access '/Users/yourslewis/.openclaw/workspace/memory/2026-03-14.md'
2026-03-15T22:21:31.664-07:00 [tools] read failed: ENOENT: no such file or directory, access '/Users/yourslewis/.openclaw/workspace/MEMORY.md'
2026-03-15T22:45:35.437-07:00 [agent/embedded] embedded run agent end: runId=b240c956-33db-4bb3-9b87-76b953a9d2cc isError=true error=Unknown error
2026-03-15T22:51:28.448-07:00 [agent/embedded] embedded run agent end: runId=bbe09fa1-c314-4235-a6b9-2e946a44ed56 isError=true error=Unknown error
2026-03-15T22:51:46.360-07:00 [agent/embedded] embedded run agent end: runId=b5e498e2-c0b1-4bd0-bb95-de50132f48b0 isError=true error=Unknown error
2026-03-15T22:52:01.837-07:00 [agent/embedded] embedded run agent end: runId=27d809e2-9481-4fa1-ab39-061e3dcf6aa7 isError=true error=Unknown error
2026-03-15T22:53:27.062-07:00 Config warnings:\n- plugins.entries.ollama: plugin ollama: plugin id mismatch (manifest uses "ollama", entry hints "ollama-provider")
- plugins.entries.sglang: plugin sglang: plugin id mismatch (manifest uses "sglang", entry hints "sglang-provider")
- plugins.entries.vllm: plugin vllm: plugin id mismatch (manifest uses "vllm", entry hints "vllm-provider")
2026-03-15T22:53:33.380-07:00 [bonjour] gateway name conflict resolved; newName="WH-HOME-MINI’s Mac mini (OpenClaw) (3)"
2026-03-15T22:53:33.387-07:00 [bonjour] gateway hostname conflict resolved; newHostname="openclaw-(3)"
2026-03-15T22:55:12.045-07:00 [tools] exec failed: zsh:1: command not found: rg

Command not found
2026-03-15T22:55:46.714-07:00 [agent/embedded] embedded run agent end: runId=e5a212b8-4b44-45a0-bab0-1811990ec0a8 isError=true model=gpt-5.4 provider=azure-gpt-5.4 error=Unknown error (no error details in response)
2026-03-15T22:57:37.576-07:00 [tools] read failed: ENOENT: no such file or directory, access '/Users/yourslewis/.openclaw/workspace/kaggle/playground-series-s6e3/full_seed_ensemble_group_all.py'
2026-03-15T22:57:37.583-07:00 [tools] read failed: ENOENT: no such file or directory, access '/Users/yourslewis/.openclaw/workspace/kaggle/playground-series-s6e3/raw_plus_smoothed_target_encoding_models.py'
2026-03-15T23:01:36.881-07:00 [tools] read failed: ENOENT: no such file or directory, access '/Users/yourslewis/.openclaw/workspace/kaggle/playground-series-s6e3/outputs/catboost_group_all_tuning_report.json'
2026-03-15T23:01:59.796-07:00 [agent/embedded] embedded run agent end: runId=cb095e39-eac9-4fa1-a81f-3364cc6ec090 isError=true model=gpt-5.4 provider=azure-gpt-5.4 error=Unknown error (no error details in response)
2026-03-15T23:20:49.122-07:00 [agent/embedded] embedded run agent end: runId=cfb02385-4c27-41eb-acda-69bc360c97e7 isError=true model=gpt-5.4 provider=azure-gpt-5.4 error=Unknown error (no error details in response)
2026-03-15T23:25:11.990-07:00 [agent/embedded] embedded run agent end: runId=352d56bb-1eca-4e23-9d08-21f44f2f6b18 isError=true model=gpt-5.4 provider=azure-gpt-5.4 error=Unknown error (no error details in response)
2026-03-15T23:50:38.421-07:00 [agent/embedded] embedded run agent end: runId=0387721d-8c14-4b78-917d-f52e1b205e5d isError=true model=gpt-5.4 provider=azure-gpt-5.4 error=Unknown error (no error details in response)
2026-03-15T23:53:56.778-07:00 [agent/embedded] embedded run agent end: runId=f6244277-fd3b-400b-beba-09e41a4a6399 isError=true model=gpt-5.4 provider=azure-gpt-5.4 error=terminated
2026-03-15T23:55:47.476-07:00 [agent/embedded] embedded run agent end: runId=5483ff35-168a-4ee4-ba5c-0da476b5165c isError=true model=gpt-5.4 provider=azure-gpt-5.4 error=Unknown error (no error details in response)
2026-03-16T00:05:59.570-07:00 [agent/embedded] embedded run agent end: runId=86ba58dc-8f74-49e8-9eb8-fa46de037177 isError=true model=gpt-5.4 provider=azure-gpt-5.4 error=Unknown error (no error details in response)
2026-03-16T00:10:50.548-07:00 [agent/embedded] embedded run agent end: runId=55f84eeb-06de-4076-aa13-95c4197e57f4 isError=true model=gpt-5.4 provider=azure-gpt-5.4 error=Unknown error (no error details in response)
2026-03-16T00:12:46.030-07:00 [agent/embedded] embedded run agent end: runId=d0011154-c46a-4176-892e-094ecaa1188a isError=true model=gpt-5.4 provider=azure-gpt-5.4 error=Unknown error (no error details in response)
2026-03-16T00:29:56.238-07:00 [agent/embedded] embedded run agent end: runId=895f70b4-7890-4f3c-87b9-ee7187dfa730 isError=true model=gpt-5.4 provider=azure-gpt-5.4 error=Unknown error (no error details in response)
2026-03-16T00:32:52.888-07:00 [agent/embedded] embedded run agent end: runId=09254b2f-402b-49fd-8f8b-55a18bca4dca isError=true model=gpt-5.4 provider=azure-gpt-5.4 error=Unknown error (no error details in response)
2026-03-16T00:34:25.641-07:00 [agent/embedded] embedded run agent end: runId=9fb47f40-7144-47a9-a2f7-a233b441dfb0 isError=true model=gpt-5.4 provider=azure-gpt-5.4 error=Unknown error (no error details in response)
2026-03-16T00:34:40.266-07:00 [agent/embedded] embedded run agent end: runId=f69802ad-6358-4f1a-aaa9-74f037167318 isError=true model=gpt-5.4 provider=azure-gpt-5.4 error=Unknown error (no error details in response)
2026-03-16T00:37:51.665-07:00 [agent/embedded] embedded run agent end: runId=55d3c47f-295a-4335-8579-0ec387a9485d isError=true model=gpt-5.4 provider=azure-gpt-5.4 error=The server had an error processing your request. Sorry about that! You can retry your request, or contact us through an Azure support request at: https://go.microsoft.com/fwlink/?linkid=2213926 if you keep seeing this error. (Please include the request ID 10d668f7-be1a-4a73-b8c1-a077aec3439f in your email.)
2026-03-16T00:40:36.080-07:00 [agent/embedded] embedded run agent end: runId=c3fccb20-656c-4ad5-bf6f-f00283651037 isError=true model=gpt-5.4 provider=azure-gpt-5.4 error=Unknown error (no error details in response)
2026-03-16T00:41:21.211-07:00 [agent/embedded] embedded run agent end: runId=bb4218a7-c367-49ac-980c-51f3250ed2d3 isError=true model=gpt-5.4 provider=azure-gpt-5.4 error=Unknown error (no error details in response)
2026-03-16T00:42:45.868-07:00 [agent/embedded] embedded run agent end: runId=dd4b8aee-9081-41cc-96f6-07cb5ead0137 isError=true model=gpt-5.4 provider=azure-gpt-5.4 error=Unknown error (no error details in response)
2026-03-16T00:47:18.535-07:00 [agent/embedded] embedded run agent end: runId=slug-gen-1773647229778 isError=true model=gpt-5.4 provider=openai-codex error=⚠️ API rate limit reached. Please try again later.
2026-03-16T00:47:18.551-07:00 [agent/embedded] auth profile failure state updated: runId=slug-gen-1773647229778 profile=sha256:06bfb5171eff provider=openai-codex reason=rate_limit window=cooldown reused=false
2026-03-16T00:47:18.557-07:00 [agent/embedded] embedded run failover decision: runId=slug-gen-1773647229778 stage=assistant decision=surface_error reason=rate_limit provider=openai-codex/gpt-5.4 profile=sha256:06bfb5171eff
2026-03-16T00:50:40.953-07:00 [agent/embedded] embedded run agent end: runId=slug-gen-1773647432517 isError=true model=gpt-5.4 provider=openai-codex error=⚠️ API rate limit reached. Please try again later.
2026-03-16T00:50:40.967-07:00 [agent/embedded] auth profile failure state updated: runId=slug-gen-1773647432517 profile=sha256:06bfb5171eff provider=openai-codex reason=rate_limit window=cooldown reused=false
2026-03-16T00:50:40.972-07:00 [agent/embedded] embedded run failover decision: runId=slug-gen-1773647432517 stage=assistant decision=surface_error reason=rate_limit provider=openai-codex/gpt-5.4 profile=sha256:06bfb5171eff
2026-03-16T00:50:56.735-07:00 [tools] read failed: ENOENT: no such file or directory, access '/Users/yourslewis/.openclaw/workspace/memory/2026-03-16.md'
2026-03-16T00:50:56.743-07:00 [tools] read failed: ENOENT: no such file or directory, access '/Users/yourslewis/.openclaw/workspace/MEMORY.md'
2026-03-16T00:52:03.060-07:00 [tools] exec failed: zsh:1: command not found: rg

Command not found
2026-03-16T01:02:33.712-07:00 [tools] gateway failed: raw required
2026-03-16T01:02:43.745-07:00 Config overwrite: /Users/yourslewis/.openclaw/openclaw.json (sha256 f2b7bae89244e54decf0f73919b4b46efecba83c2448ea83b8345df2b73310b5 -> 5d33249aa3c68664454200e95afbbed4ef4c57509e5fc164fae1b80dd60d9db6, backup=/Users/yourslewis/.openclaw/openclaw.json.bak)
2026-03-16T01:02:44.288-07:00 [reload] config change requires gateway restart (plugins.entries.acpx, acp) — deferring until 2 operation(s), 1 embedded run(s) complete
2026-03-16T01:03:07.403-07:00 [agent/embedded] embedded run agent end: runId=1388f1a7-379b-47a3-aa72-8ffbea11bf1e isError=true model=gpt-5.4 provider=azure-gpt-5.4 error=Unknown error (no error details in response)
2026-03-16T01:03:10.762-07:00 [plugins] acpx local binary unavailable or mismatched (acpx command not found at /opt/homebrew/lib/node_modules/openclaw/extensions/acpx/node_modules/.bin/acpx); running plugin-local install
2026-03-16T01:03:13.663-07:00 [bonjour] gateway name conflict resolved; newName="WH-HOME-MINI’s Mac mini (OpenClaw) (3)"
2026-03-16T01:03:13.670-07:00 [bonjour] gateway hostname conflict resolved; newHostname="openclaw-(3)"
2026-03-16T01:03:24.499-07:00 [agent/embedded] embedded run agent end: runId=slug-gen-1773648195740 isError=true model=gpt-5.4 provider=openai-codex error=⚠️ API rate limit reached. Please try again later.
2026-03-16T01:03:24.510-07:00 [agent/embedded] auth profile failure state updated: runId=slug-gen-1773648195740 profile=sha256:06bfb5171eff provider=openai-codex reason=rate_limit window=cooldown reused=false
2026-03-16T01:03:24.513-07:00 [agent/embedded] embedded run failover decision: runId=slug-gen-1773648195740 stage=assistant decision=surface_error reason=rate_limit provider=openai-codex/gpt-5.4 profile=sha256:06bfb5171eff
2026-03-16T01:03:40.628-07:00 [tools] read failed: ENOENT: no such file or directory, access '/Users/yourslewis/.openclaw/workspace/memory/2026-03-16.md'
2026-03-16T01:03:40.636-07:00 [tools] read failed: ENOENT: no such file or directory, access '/Users/yourslewis/.openclaw/workspace/MEMORY.md'
2026-03-16T01:16:40.218-07:00 [tools] exec failed: elevated is not available right now (runtime=direct).
Failing gates: allowFrom (tools.elevated.allowFrom.<provider> / agents.list[].tools.elevated.allowFrom.<provider>)
Context: provider=telegram session=agent:main:telegram:direct:7166306868
Fix-it keys:
- tools.elevated.enabled
- tools.elevated.allowFrom.<provider>
- agents.list[].tools.elevated.enabled
- agents.list[].tools.elevated.allowFrom.<provider>
2026-03-16T01:17:32.526-07:00 [agent/embedded] embedded run agent end: runId=5884fd8a-3b21-4930-81e8-db6d7b36297f isError=true model=gpt-5.4 provider=azure-gpt-5.4 error=Unknown error (no error details in response)
2026-03-16T01:40:33.669-07:00 [tools] exec failed: zsh:1: command not found: python

Command not found
2026-03-16T02:04:05.086-07:00 [agent/embedded] embedded run agent end: runId=7bdc45b1-19c8-4efc-809a-65554ddb16df isError=true model=gpt-5.4 provider=azure-gpt-5.4 error=Unknown error (no error details in response)
2026-03-16T02:38:12.612-07:00 [agent/embedded] embedded run agent end: runId=53b58481-f9ed-43b0-8240-5b3684319f83 isError=true model=gpt-5.4 provider=azure-gpt-5.4 error=Unknown error (no error details in response)
2026-03-16T02:40:01.787-07:00 [agent/embedded] embedded run agent end: runId=a4e9320a-cca7-47ca-b54d-dd4b856ecc88 isError=true model=gpt-5.4 provider=azure-gpt-5.4 error=Unknown error (no error details in response)
2026-03-16T02:40:14.256-07:00 [agent/embedded] embedded run agent end: runId=4529913d-b90f-4b11-b549-34ae339877e0 isError=true model=gpt-5.4 provider=azure-gpt-5.4 error=Unknown error (no error details in response)
2026-03-16T02:45:44.133-07:00 [agent/embedded] embedded run agent end: runId=d77093bd-87fc-4bbf-8a12-50d1c359d495 isError=true model=gpt-5.4 provider=azure-gpt-5.4 error=Unknown error (no error details in response)
2026-03-16T02:49:47.895-07:00 [agent/embedded] embedded run agent end: runId=867cd961-692c-48f1-b1c2-bd1ba6cd1021 isError=true model=gpt-5.4 provider=azure-gpt-5.4 error=Unknown error (no error details in response)
2026-03-16T02:58:38.446-07:00 [agent/embedded] embedded run agent end: runId=8467aacf-293c-44d4-89f1-5c2e8b1074c2 isError=true model=gpt-5.4 provider=azure-gpt-5.4 error=Unknown error (no error details in response)
2026-03-16T03:08:06.055-07:00 [agent/embedded] embedded run agent end: runId=0de8b6c9-1ced-418a-a981-e40c0610a990 isError=true model=gpt-5.4 provider=azure-gpt-5.4 error=Unknown error (no error details in response)
2026-03-16T03:09:29.170-07:00 [agent/embedded] embedded run agent end: runId=e33f56ac-00f8-4c7c-b764-33604352eeeb isError=true model=gpt-5.4 provider=azure-gpt-5.4 error=Unknown error (no error details in response)
2026-03-16T03:09:50.269-07:00 [agent/embedded] embedded run agent end: runId=7d5f8a94-aa23-40b1-9a3c-ac44c698410d isError=true model=gpt-5.4 provider=azure-gpt-5.4 error=Unknown error (no error details in response)
2026-03-16T03:28:52.629-07:00 [gateway] security audit: device access upgrade requested reason=scope-upgrade device=21e5a951755a4c56cad224a94fc5c74c3676fd96b6231d7a685cd30e8294261c ip=unknown-ip auth=token roleFrom=operator roleTo=operator scopesFrom=operator.read scopesTo=operator.admin,operator.approvals,operator.pairing,operator.read,operator.write client=cli conn=de44ce49-661d-4baa-b2b8-82016d248c8c
2026-03-16T03:29:01.566-07:00 [plugins] acpx local binary unavailable or mismatched (acpx command not found at /opt/homebrew/lib/node_modules/openclaw/extensions/acpx/node_modules/.bin/acpx); running plugin-local install
2026-03-16T03:29:04.341-07:00 [bonjour] gateway name conflict resolved; newName="WH-HOME-MINI’s Mac mini (OpenClaw) (3)"
2026-03-16T03:29:04.345-07:00 [bonjour] gateway hostname conflict resolved; newHostname="openclaw-(3)"
2026-03-16T03:48:22.095-07:00 [agent/embedded] embedded run agent end: runId=80eb5115-747d-4399-b091-ed2ea204e88e isError=true model=gpt-5.4 provider=azure-gpt-5.4 error=Unknown error (no error details in response)
2026-03-16T03:49:00.601-07:00 [compaction] Full summarization failed, trying partial: Summarization failed: Unknown error (no error details in response)
2026-03-16T03:49:04.527-07:00 [compaction] Partial summarization also failed: Summarization failed: Unknown error (no error details in response)
2026-03-16T03:49:07.619-07:00 [compaction] Full summarization failed, trying partial: Summarization failed: Unknown error (no error details in response)
2026-03-16T03:49:10.570-07:00 [compaction] Partial summarization also failed: Summarization failed: Unknown error (no error details in response)
2026-03-16T03:49:44.694-07:00 [tools] read failed: ENOENT: no such file or directory, access '/Users/yourslewis/.openclaw/workspace/MEMORY.md'
2026-03-16T03:53:05.345-07:00 [agent/embedded] embedded run agent end: runId=b737cb93-84d4-4340-859d-bdcc38a583b0 isError=true model=gpt-5.4 provider=azure-gpt-5.4 error=Unknown error (no error details in response)
2026-03-16T05:35:49.903-07:00 [bonjour] gateway name conflict resolved; newName="WH-HOME-MINI’s Mac mini (OpenClaw) (3)"
2026-03-16T05:35:49.909-07:00 [bonjour] gateway hostname conflict resolved; newHostname="openclaw-(3)"
2026-03-16T07:42:35.137-07:00 [tools] read failed: ENOENT: no such file or directory, access '/Users/yourslewis/.openclaw/workspace/MEMORY.md'
2026-03-16T09:39:36.541-07:00 [tools] exec failed: zsh:1: command not found: python

Command not found
2026-03-16T09:39:37.642-07:00 [agent/embedded] embedded run agent end: runId=f4833bca-3c24-4e30-bb97-eb1d83bee598 isError=true model=gpt-5.4 provider=azure-gpt-5.4 error=Unknown error (no error details in response)
2026-03-16T11:02:39.162-07:00 [agent/embedded] embedded run agent end: runId=7daeb2c7-9441-4db4-a7a7-e9eed824c8ba isError=true model=gpt-5.4 provider=azure-gpt-5.4 error=Unknown error (no error details in response)
2026-03-16T11:02:40.821-07:00 [agent/embedded] embedded run agent end: runId=b89e53d3-6919-46a5-8f28-02eb40c5d150 isError=true model=gpt-5.4 provider=azure-gpt-5.4 error=Unknown error (no error details in response)
2026-03-16T11:03:47.462-07:00 [compaction] Full summarization failed, trying partial: Summarization failed: Unknown error (no error details in response)
2026-03-16T11:03:51.221-07:00 [compaction] Partial summarization also failed: Summarization failed: Unknown error (no error details in response)
2026-03-16T11:03:55.282-07:00 [compaction] Full summarization failed, trying partial: Summarization failed: Unknown error (no error details in response)
2026-03-16T11:03:58.343-07:00 [compaction] Partial summarization also failed: Summarization failed: Unknown error (no error details in response)
2026-03-16T11:05:10.850-07:00 [tools] read failed: ENOENT: no such file or directory, access '/Users/yourslewis/.openclaw/workspace/MEMORY.md'
2026-03-16T11:05:35.118-07:00 [tools] read failed: ENOENT: no such file or directory, access '/Users/yourslewis/.openclaw/workspace/MEMORY.md'
2026-03-16T11:14:13.470-07:00 [tools] exec failed: /Users/yourslewis/.openclaw/workspace
total 120
drwxr-xr-x  18 yourslewis  staff    576 Mar 16 02:31 .
drwx------  23 yourslewis  staff    736 Mar 16 01:05 ..
-rw-r--r--@  1 yourslewis  staff  12292 Mar 12 10:51 .DS_Store
drwxr-xr-x  12 yourslewis  staff    384 Mar 16 02:32 .git
drwxr-xr-x   3 yourslewis  staff     96 Mar  7 03:31 .openclaw
drwx------  10 yourslewis  staff    320 Mar 11 17:46 .venv
-rw-r--r--   1 yourslewis  staff   7869 Mar  7 03:31 AGENTS.md
-rw-r--r--   1 yourslewis  staff   1470 Mar  7 03:31 BOOTSTRAP.md
-rw-------   1 yourslewis  staff   4846 Mar 16 00:27 GPU_HOST_OPTION_1B.md
-rw-r--r--   1 yourslewis  staff    168 Mar  7 03:31 HEARTBEAT.md
-rw-r--r--   1 yourslewis  staff    636 Mar  7 03:31 IDENTITY.md
-rw-r--r--   1 yourslewis  staff   1673 Mar  7 03:31 SOUL.md
-rw-------   1 yourslewis  staff   3393 Mar 16 02:31 TMUX_OPENCLAW_WORKFLOW.md
-rw-r--r--   1 yourslewis  staff   1018 Mar 16 02:31 TOOLS.md
-rw-r--r--   1 yourslewis  staff    730 Mar 16 02:31 USER.md
drwx------   9 yourslewis  staff    288 Mar 11 18:08 catboost_info
drwx------   4 yourslewis  staff    128 Mar 11 19:54 kaggle
drwx------   6 yourslewis  staff    192 Mar 16 01:35 memory
 M memory/2026-03-16.md
?? .DS_Store
?? .openclaw/
?? AGENTS.md
?? BOOTSTRAP.md
?? HEARTBEAT.md
?? IDENTITY.md
?? SOUL.md
?? catboost_info/
?? kaggle/.DS_Store
?? kaggle/playground-series-s6e3/__pycache__/
?? kaggle/playground-series-s6e3/analyze_misclassified_feature_coverage.py
?? kaggle/playground-series-s6e3/analyze_training_data_cleansing.py
?? kaggle/playground-series-s6e3/batch1_feature_engineering_catboost.py
?? kaggle/playground-series-s6e3/batch2_grouped_stats_catboost.py
?? kaggle/playground-series-s6e3/catboost_info/
?? kaggle/playground-series-s6e3/exp2_top_pairs.py
?? kaggle/playground-series-s6e3/experiment_raw_vs_ohe.py
?? kaggle/playground-series-s6e3/outputs/batch1_feature_engineering_report.json
?? kaggle/playground-series-s6e3/outputs/batch1_feature_engineering_results.csv
?? kaggle/playground-series-s6e3/outputs/batch2_grouped_stats_report.json
?? kaggle/playground-series-s6e3/outputs/batch2_grouped_stats_results.csv
?? kaggle/playground-series-s6e3/outputs/catboost_auc_ctr_multismooth/
?? kaggle/playground-series-s6e3/outputs/catboost_full_train_raw_plus_smoothed_te_report.json
?? kaggle/playground-series-s6e3/outputs/contract_experts_report.json
?? kaggle/playground-series-s6e3/outputs/cv_best_catboost_submission_report.json
?? kaggle/playground-series-s6e3/outputs/cv_screen/
?? kaggle/playground-series-s6e3/outputs/data_cleansing_experiments.json
?? kaggle/playground-series-s6e3/outputs/exp2_top_pairs_report.json
?? kaggle/playground-series-s6e3/outputs/exp2_top_pairs_results.csv
?? kaggle/playground-series-s6e3/outputs/exp5_single_feature_accuracy.json
?? kaggle/playground-series-s6e3/outputs/exp_raw_vs_ohe_report.json
?? kaggle/playground-series-s6e3/outputs/exp_raw_vs_ohe_results.csv
?? kaggle/playground-series-s6e3/outputs/full_seed_ensemble_group_all/
?? kaggle/playground-series-s6e3/outputs/full_seed_ensemble_tuned_single/
?? kaggle/playground-series-s6e3/outputs/misclassified_feature_coverage.json
?? kaggle/playground-series-s6e3/outputs/misclassified_only_training_report.json
?? kaggle/playground-series-s6e3/outputs/pairwise_combination_stats_study.json
?? kaggle/playground-series-s6e3/outputs/pairwise_group_stats_experiment.json
?? kaggle/playground-series-s6e3/outputs/random_subspace_majority_vote_50pct_M13.json
?? kaggle/playground-series-s6e3/outputs/raw_plus_smoothed_target_encoding_models_report.json
?? kaggle/playground-series-s6e3/outputs/raw_plus_smoothed_target_encoding_models_results.csv
?? kaggle/playground-series-s6e3/outputs/raw_plus_target_encoding_models_report.json
?? kaggle/playground-series-s6e3/outputs/raw_plus_target_encoding_models_results.csv
?? kaggle/playground-series-s6e3/outputs/seed_ensemble_group_all/
?? kaggle/playground-series-s6e3/outputs/single_pair_lift_report.json
?? kaggle/playground-series-s6e3/outputs/single_pair_lift_results.csv
?? kaggle/playground-series-s6e3/outputs/stack_logreg_test_preds.csv
?? kaggle/playground-series-s6e3/outputs/stack_simple_average_test_preds.csv
?? kaggle/playground-series-s6e3/outputs/stack_weighted_average_test_preds.csv
?? kaggle/playground-series-s6e3/outputs/stacking_combinations_report.json
?? kaggle/playground-series-s6e3/outputs/stacking_combinations_results.csv
?? kaggle/playground-series-s6e3/outputs/stacking_prep/
?? kaggle/playground-series-s6e3/outputs/submission_catboost_full_train_raw_plus_smoothed_te.csv
?? kaggle/playground-series-s6e3/outputs/submission_catboost_raw_plus_smoothed_target_encoding.csv
?? kaggle/playground-series-s6e3/outputs/submission_catboost_raw_plus_target_encoding.csv
?? kaggle/playground-series-s6e3/outputs/submission_catboost_target_encoding.csv
?? kaggle/playground-series-s6e3/outputs/submission_cv_best_catboost.csv
?? kaggle/playground-series-s6e3/outputs/submission_exp1_cat_raw.csv
?? kaggle/playground-series-s6e3/outputs/submission_exp2_cat_ohe.csv
?? kaggle/playground-series-s6e3/outputs/submission_exp2_top1_pair.csv
?? kaggle/playground-series-s6e3/outputs/submission_exp2_top2_pairs.csv
?? kaggle/playground-series-s6e3/outputs/submission_exp2_top4_pairs.csv
?? kaggle/playground-series-s6e3/outputs/submission_exp3_xgb_ohe.csv
?? kaggle/playground-series-s6e3/outputs/submission_exp4_lgb_ohe.csv
?? kaggle/playground-series-s6e3/outputs/submission_exp5_cat_ohe_pairs.csv
?? kaggle/playground-series-s6e3/outputs/submission_lightgbm_raw_plus_smoothed_target_encoding.csv
?? kaggle/playground-series-s6e3/outputs/submission_lightgbm_raw_plus_target_encoding.csv
?? kaggle/playground-series-s6e3/outputs/submission_lightgbm_target_encoding.csv
?? kaggle/playground-series-s6e3/outputs/submission_transformer_hybrid_tuned.csv
?? kaggle/playground-series-s6e3/outputs/submission_transformer_t1.csv
?? kaggle/playground-series-s6e3/outputs/submission_transformer_t1_mmoe.csv
?? kaggle/playground-series-s6e3/outputs/submission_transformer_t1_single_task_moe.csv
?? kaggle/playground-series-s6e3/outputs/target_encoding_maps_preview.json
?? kaggle/playground-series-s6e3/outputs/target_encoding_models_report.json
?? kaggle/playground-series-s6e3/outputs/target_encoding_models_results.csv
?? kaggle/playground-series-s6e3/outputs/training_data_cleansing_report.json
?? kaggle/playground-series-s6e3/outputs/transformer_hybrid_tuned_report.json
?? kaggle/playground-series-s6e3/outputs/transformer_lr_sweep_report.json
?? kaggle/playground-series-s6e3/outputs/transformer_lr_sweep_results.csv
?? kaggle/playground-series-s6e3/outputs/transformer_short_sweep_report.json
?? kaggle/playground-series-s6e3/outputs/transformer_short_sweep_results.csv
?? kaggle/playground-series-s6e3/outputs/transformer_t1_mmoe_report.json
?? kaggle/playground-series-s6e3/outputs/transformer_t1_report.json
?? kaggle/playground-series-s6e3/outputs/transformer_t1_single_task_moe_report.json
?? kaggle/playground-series-s6e3/pairwise_combination_stats_study.py
?? kaggle/playground-series-s6e3/run_contract_experts.py
?? kaggle/playground-series-s6e3/run_cv_screen.py
?? kaggle/playground-series-s6e3/run_cv_screen_catboost.py
?? kaggle/playground-series-s6e3/run_data_cleansing_experiments.py
?? kaggle/playground-series-s6e3/run_misclassified_only_training.py
?? kaggle/playground-series-s6e3/run_pairwise_group_stats_exp.py
?? kaggle/playground-series-s6e3/run_random_subspace_majority_vote.py
?? kaggle/playground-series-s6e3/run_stacking_combinations.py
?? kaggle/playground-series-s6e3/sample_submission.csv
?? kaggle/playground-series-s6e3/seed_ensemble_group_all_catboost.py
?? kaggle/playground-series-s6e3/stacking_prep_oof.py
?? kaggle/playground-series-s6e3/stacking_prep_plan.md
?? kaggle/playground-series-s6e3/sweep_single_pair_lift.py
?? kaggle/playground-series-s6e3/sweep_transformer_lrs.py
?? kaggle/playground-series-s6e3/sweep_transformer_short.py
?? kaggle/playground-series-s6e3/test.csv
?? kaggle/playground-series-s6e3/train.csv
?? kaggle/playground-series-s6e3/train_full_best_catboost_submission.py
?? kaggle/playground-series-s6e3/train_full_cv_best_submission.py
?? kaggle/playground-series-s6e3/train_full_seed_ensemble_group_all.py
?? kaggle/playground-series-s6e3/train_full_seed_ensemble_tuned_single.py
?? kaggle/playground-series-s6e3/train_raw_plus_smoothed_target_encoding_models.py
?? kaggle/playground-series-s6e3/train_raw_plus_target_encoding_models.py
?? kaggle/playground-series-s6e3/train_tabular_transformer.py
?? kaggle/playground-series-s6e3/train_tabular_transformer_t1_bestdir.py
?? kaggle/playground-series-s6e3/train_tabular_transformer_t1_t2.py
?? kaggle/playground-series-s6e3/train_target_encoding_models.py
?? kaggle/playground-series-s6e3/tune_catboost_group_all.py
?? memory/2026-03-11-churn-dataset.md
?? memory/2026-03-15.md
?? memory/2026-03-16-api-rate-limit-reached-please-.md
---
total 2734344
drwx------  50 yourslewis  staff       1600 Mar 16 03:33 .
drwx------   4 yourslewis  staff        128 Mar 11 19:54 ..
drwx------   6 yourslewis  staff        192 Mar 15 23:20 __pycache__
-rw-------   1 yourslewis  staff       6386 Mar 14 12:51 analyze_misclassified_feature_coverage.py
-rw-------   1 yourslewis  staff       5237 Mar 14 08:53 analyze_training_data_cleansing.py
-rw-------   1 yourslewis  staff      10209 Mar 13 00:12 batch1_feature_engineering_catboost.py
-rw-------   1 yourslewis  staff       6967 Mar 13 02:07 batch2_grouped_stats_catboost.py
drwx------   9 yourslewis  staff        288 Mar 16 02:10 catboost_info
-rw-------   1 yourslewis  staff       5622 Mar 12 07:28 exp2_top_pairs.py
-rw-------   1 yourslewis  staff      10066 Mar 11 23:50 experiment_raw_vs_ohe.py
drwx------  95 yourslewis  staff       3040 Mar 16 03:35 outputs
-rw-------   1 yourslewis  staff       6439 Mar 13 16:52 pairwise_combination_stats_study.py
-rw-------   1 yourslewis  staff      11992 Mar 15 23:20 run_catboost_auc_ctr_multismooth.py
-rw-------   1 yourslewis  staff       6243 Mar 14 14:46 run_contract_experts.py
-rw-------   1 yourslewis  staff      10108 Mar 16 02:41 run_cv_screen.py
-rw-------   1 yourslewis  staff      11103 Mar 16 03:04 run_cv_screen_catboost.py
-rw-------   1 yourslewis  staff       7131 Mar 14 09:00 run_data_cleansing_experiments.py
-rw-------   1 yourslewis  staff       7088 Mar 14 11:07 run_misclassified_only_training.py
-rw-------   1 yourslewis  staff       6548 Mar 13 22:24 run_pairwise_group_stats_exp.py
-rw-------   1 yourslewis  staff       7347 Mar 13 23:53 run_random_subspace_majority_vote.py
-rw-------   1 yourslewis  staff       3417 Mar 13 11:06 run_stacking_combinations.py
-rw-------   1 yourslewis  staff    2291904 Feb 24 00:01 sample_submission.csv
-rw-------   1 yourslewis  staff       7082 Mar 16 02:03 seed_ensemble_group_all_catboost.py
-rw-------   1 yourslewis  staff       8006 Mar 13 08:55 stacking_prep_oof.py
-rw-------   1 yourslewis  staff       1047 Mar 13 08:54 stacking_prep_plan.md
-rw-------   1 yourslewis  staff       5225 Mar 12 00:29 sweep_single_pair_lift.py
-rw-------   1 yourslewis  staff       9685 Mar 12 10:51 sweep_transformer_lrs.py
-rw-------   1 yourslewis  staff      11431 Mar 15 11:31 sweep_transformer_short.py
-rw-------   1 yourslewis  staff   33762450 Feb 24 00:01 test.csv
-rw-------   1 yourslewis  staff  385087143 Mar 11 23:05 test_pairwise_cats.csv
-rw-------   1 yourslewis  staff   80512352 Feb 24 00:01 train.csv
-rw-------   1 yourslewis  staff      10414 Mar 11 18:07 train_baselines.py
-rw-------   1 yourslewis  staff       3218 Mar 12 21:42 train_full_best_catboost_submission.py
-rw-------   1 yourslewis  staff       4926 Mar 16 03:33 train_full_cv_best_submission.py
-rw-------   1 yourslewis  staff       4845 Mar 13 13:17 train_full_seed_ensemble_group_all.py
-rw-------   1 yourslewis  staff       4805 Mar 14 02:13 train_full_seed_ensemble_tuned_single.py
-rw-------   1 yourslewis  staff      18769 Mar 15 16:06 train_hybrid_transformer_tuned.py
-rw-------   1 yourslewis  staff  897928073 Mar 11 23:05 train_pairwise_cats.csv
-rw-------   1 yourslewis  staff       3578 Mar 12 08:34 train_random_forest_best_features.py
-rw-------   1 yourslewis  staff       7629 Mar 12 20:48 train_raw_plus_smoothed_target_encoding_models.py
-rw-------   1 yourslewis  staff       7097 Mar 12 19:24 train_raw_plus_target_encoding_models.py
-rw-------   1 yourslewis  staff      15941 Mar 15 18:34 train_t1_mmoe.py
-rw-------   1 yourslewis  staff      15036 Mar 15 19:50 train_t1_single_task_moe.py
-rw-------   1 yourslewis  staff      11226 Mar 12 09:28 train_tabular_transformer.py
-rw-------   1 yourslewis  staff      11515 Mar 15 14:37 train_tabular_transformer_t1_bestdir.py
-rw-------   1 yourslewis  staff      18219 Mar 15 06:53 train_tabular_transformer_t1_t2.py
-rw-------   1 yourslewis  staff       6460 Mar 12 19:12 train_target_encoding_models.py
-rw-------   1 yourslewis  staff       8002 Mar 11 23:08 train_with_pairwise_cats.py
-rw-------   1 yourslewis  staff       8077 Mar 11 20:24 tune_baselines.py
-rw-------   1 yourslewis  staff       5212 Mar 13 16:59 tune_catboost_group_all.py
---
zsh:1: command not found: rg

Command not found
2026-03-16T11:14:33.514-07:00 [agent/embedded] embedded run agent end: runId=12895214-904c-4cda-92f1-3f2db3321f25 isError=true model=gpt-5.4 provider=azure-gpt-5.4 error=Unknown error (no error details in response)
2026-03-16T12:11:54.659-07:00 [compaction] Full summarization failed, trying partial: Summarization failed: Unknown error (no error details in response)
2026-03-16T12:11:58.073-07:00 [compaction] Partial summarization also failed: Summarization failed: Unknown error (no error details in response)
2026-03-16T12:17:24.348-07:00 [agent/embedded] embedded run agent end: runId=2faae740-b94f-4c5f-9828-6cdaacc4eec5 isError=true model=gpt-5.4 provider=azure-gpt-5.4 error=Unknown error (no error details in response)
2026-03-16T12:17:25.805-07:00 [agent/embedded] embedded run agent end: runId=e777f008-a2b1-404a-8e47-23480a602315 isError=true model=gpt-5.4 provider=azure-gpt-5.4 error=Unknown error (no error details in response)
2026-03-16T12:20:36.248-07:00 [tools] read failed: ENOENT: no such file or directory, access '/Users/yourslewis/.openclaw/workspace/MEMORY.md'
2026-03-16T14:59:59.322-07:00 [tools] read failed: ENOENT: no such file or directory, access '/Users/yourslewis/.openclaw/workspace/MEMORY.md'
2026-03-16T14:59:59.325-07:00 [tools] read failed: ENOENT: no such file or directory, access '/Users/yourslewis/.openclaw/workspace/kaggle/playground-series-s6e3/outputs/cv_screen_multiseed/cv_screen_multiseed_report.json'
2026-03-16T15:00:01.107-07:00 [agent/embedded] embedded run agent end: runId=04c9c1f9-c42f-40e4-9af2-40523eda5eb4 isError=true model=gpt-5.4 provider=azure-gpt-5.4 error=Unknown error (no error details in response)
2026-03-16T19:23:37.471-07:00 [tools] read failed: ENOENT: no such file or directory, access '/Users/yourslewis/.openclaw/workspace/MEMORY.md'
2026-03-16T20:28:17.113-07:00 [telegram] fetch fallback: enabling sticky IPv4-only dispatcher (codes=UND_ERR_CONNECT_TIMEOUT)
2026-03-17T00:45:26.264-07:00 [tools] read failed: ENOENT: no such file or directory, access '/Users/yourslewis/.openclaw/workspace/memory/2026-03-17.md'
2026-03-17T00:46:04.599-07:00 [tools] read failed: ENOENT: no such file or directory, access '/Users/yourslewis/.openclaw/workspace/MEMORY.md'
2026-03-17T00:46:04.601-07:00 [tools] read failed: ENOENT: no such file or directory, access '/Users/yourslewis/.openclaw/workspace/kaggle/playground-series-s6e3/outputs/cv_candidate_batch/cv_candidate_batch_report.json'
2026-03-17T01:09:24.065-07:00 [telegram] Polling stall detected (no getUpdates for 94.21s); forcing restart.
2026-03-17T01:09:24.083-07:00 [telegram] polling runner stopped (polling stall detected); restarting in 2.13s.
2026-03-17T11:32:04.433-07:00 [bonjour] gateway name conflict resolved; newName="WH-HOME-MINI’s Mac mini (OpenClaw) (3)"
2026-03-17T11:32:04.442-07:00 [bonjour] gateway hostname conflict resolved; newHostname="openclaw-(3)"
2026-03-17T11:34:35.494-07:00 [bonjour] gateway name conflict resolved; newName="WH-HOME-MINI’s Mac mini (OpenClaw) (3)"
2026-03-17T11:34:35.502-07:00 [bonjour] gateway hostname conflict resolved; newHostname="openclaw-(3)"
2026-03-17T11:35:24.947-07:00 [agent/embedded] embedded run agent end: runId=0bf777c4-f059-43a8-988b-0ea66415c711 isError=true model=claude-opus-4-6-1m provider=copilot-opus-4.6-1m error=400 litellm.BadRequestError: Github_copilotException - bad request: unknown Copilot-Integration-Id
. Received Model Group=claude-opus-4-6-1m
Available Model Group Fallbacks=None
2026-03-17T11:35:47.828-07:00 [bonjour] gateway name conflict resolved; newName="WH-HOME-MINI’s Mac mini (OpenClaw) (3)"
2026-03-17T11:35:47.836-07:00 [bonjour] gateway hostname conflict resolved; newHostname="openclaw-(3)"
2026-03-17T11:35:50.318-07:00 [agent/embedded] embedded run agent end: runId=85192f2b-b4bc-4c2d-82f3-29d43ce4f1d2 isError=true model=claude-opus-4-6-1m provider=copilot-opus-4.6-1m error=400 litellm.BadRequestError: Github_copilotException - bad request: unknown Copilot-Integration-Id
. Received Model Group=claude-opus-4-6-1m
Available Model Group Fallbacks=None
2026-03-17T11:38:25.388-07:00 [bonjour] gateway name conflict resolved; newName="WH-HOME-MINI’s Mac mini (OpenClaw) (3)"
2026-03-17T11:38:25.396-07:00 [bonjour] gateway hostname conflict resolved; newHostname="openclaw-(3)"
2026-03-17T11:38:27.305-07:00 [agent/embedded] embedded run agent end: runId=8fc70026-1def-4ab3-91f1-4dddbe8710c9 isError=true model=claude-opus-4-6-1m provider=copilot-opus-4.6-1m error=400 litellm.BadRequestError: Github_copilotException - {"error":{"message":"model claude-opus-4.6-1m does not support Responses API.","code":"unsupported_api_for_model"}}
. Received Model Group=claude-opus-4-6-1m
Available Model Group Fallbacks=None
2026-03-17T11:42:36.756-07:00 [bonjour] gateway name conflict resolved; newName="WH-HOME-MINI’s Mac mini (OpenClaw) (3)"
2026-03-17T11:42:36.763-07:00 [bonjour] gateway hostname conflict resolved; newHostname="openclaw-(3)"
2026-03-17T11:42:52.857-07:00 [tools] read failed: ENOENT: no such file or directory, access '/Users/yourslewis/.openclaw/workspace/MEMORY.md'
2026-03-17T11:46:15.107-07:00 [bonjour] gateway name conflict resolved; newName="WH-HOME-MINI’s Mac mini (OpenClaw) (3)"
2026-03-17T11:46:15.115-07:00 [bonjour] gateway hostname conflict resolved; newHostname="openclaw-(3)"
2026-03-17T11:47:35.309-07:00 [bonjour] gateway name conflict resolved; newName="WH-HOME-MINI’s Mac mini (OpenClaw) (3)"
2026-03-17T11:47:35.318-07:00 [bonjour] gateway hostname conflict resolved; newHostname="openclaw-(3)"
2026-03-17T11:56:07.866-07:00 [bonjour] gateway name conflict resolved; newName="WH-HOME-MINI’s Mac mini (OpenClaw) (3)"
2026-03-17T11:56:07.875-07:00 [bonjour] gateway hostname conflict resolved; newHostname="openclaw-(3)"
2026-03-17T11:57:07.668-07:00 [bonjour] gateway name conflict resolved; newName="WH-HOME-MINI’s Mac mini (OpenClaw) (3)"
2026-03-17T11:57:07.677-07:00 [bonjour] gateway hostname conflict resolved; newHostname="openclaw-(3)"
2026-03-17T12:19:57.012-07:00 Config overwrite: /Users/yourslewis/.openclaw/openclaw.json (sha256 a3fba6faba7f0b2e5a38136f69c37a5030170c5ef8bb1a2538f0cff2641dd624 -> 6ac4e1566fcb834af514e5fde0edc7167fe3743dc44b63ad5d74b5c7e19e5c0f, backup=/Users/yourslewis/.openclaw/openclaw.json.bak)
2026-03-17T12:19:58.637-07:00 [telegram] deleteWebhook failed: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-17T12:19:58.646-07:00 [telegram] [chloe] channel exited: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-17T12:19:58.656-07:00 [telegram] deleteMyCommands failed: Call to 'deleteMyCommands' failed! (404: Not Found)
2026-03-17T12:19:58.663-07:00 [telegram] deleteMyCommands failed: Call to 'deleteMyCommands' failed! (404: Not Found)
2026-03-17T12:19:58.667-07:00 [telegram] deleteWebhook failed: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-17T12:19:58.670-07:00 [telegram] [rex] channel exited: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-17T12:19:58.818-07:00 [telegram] setMyCommands failed: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-17T12:19:58.822-07:00 [telegram] command sync failed: GrammyError: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-17T12:19:59.140-07:00 [telegram] setMyCommands failed: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-17T12:19:59.147-07:00 [telegram] command sync failed: GrammyError: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-17T12:20:04.648-07:00 [telegram] channels.telegram: accounts.default is missing; falling back to "chloe". Set channels.telegram.defaultAccount or add channels.telegram.accounts.default to avoid routing surprises in multi-account setups.
2026-03-17T12:20:04.666-07:00 [telegram] deleteMyCommands failed: Call to 'deleteMyCommands' failed! (404: Not Found)
2026-03-17T12:20:04.677-07:00 [telegram] deleteWebhook failed: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-17T12:20:04.679-07:00 [telegram] [chloe] channel exited: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-17T12:20:05.078-07:00 [telegram] deleteMyCommands failed: Call to 'deleteMyCommands' failed! (404: Not Found)
2026-03-17T12:20:05.088-07:00 [telegram] deleteWebhook failed: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-17T12:20:05.092-07:00 [telegram] [rex] channel exited: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-17T12:20:05.137-07:00 [telegram] setMyCommands failed: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-17T12:20:05.139-07:00 [telegram] command sync failed: GrammyError: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-17T12:20:05.579-07:00 [telegram] setMyCommands failed: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-17T12:20:05.586-07:00 [telegram] command sync failed: GrammyError: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-17T12:20:10.807-07:00 [telegram] channels.telegram: accounts.default is missing; falling back to "chloe". Set channels.telegram.defaultAccount or add channels.telegram.accounts.default to avoid routing surprises in multi-account setups.
2026-03-17T12:20:12.070-07:00 [telegram] deleteWebhook failed: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-17T12:20:12.078-07:00 [telegram] [chloe] channel exited: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-17T12:20:12.087-07:00 [telegram] deleteWebhook failed: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-17T12:20:12.091-07:00 [telegram] [rex] channel exited: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-17T12:20:12.097-07:00 [telegram] deleteMyCommands failed: Call to 'deleteMyCommands' failed! (404: Not Found)
2026-03-17T12:20:12.100-07:00 [telegram] deleteMyCommands failed: Call to 'deleteMyCommands' failed! (404: Not Found)
2026-03-17T12:20:12.262-07:00 [telegram] setMyCommands failed: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-17T12:20:12.268-07:00 [telegram] command sync failed: GrammyError: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-17T12:20:12.593-07:00 [telegram] setMyCommands failed: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-17T12:20:12.598-07:00 [telegram] command sync failed: GrammyError: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-17T12:20:13.976-07:00 [bonjour] gateway name conflict resolved; newName="WH-HOME-MINI’s Mac mini (OpenClaw) (3)"
2026-03-17T12:20:13.984-07:00 [bonjour] gateway hostname conflict resolved; newHostname="openclaw-(3)"
2026-03-17T12:20:18.312-07:00 [telegram] deleteWebhook failed: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-17T12:20:18.319-07:00 [telegram] [rex] channel exited: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-17T12:20:18.328-07:00 [telegram] deleteMyCommands failed: Call to 'deleteMyCommands' failed! (404: Not Found)
2026-03-17T12:20:18.428-07:00 [telegram] deleteMyCommands failed: Call to 'deleteMyCommands' failed! (404: Not Found)
2026-03-17T12:20:18.438-07:00 [telegram] deleteWebhook failed: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-17T12:20:18.443-07:00 [telegram] [chloe] channel exited: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-17T12:20:18.488-07:00 [telegram] setMyCommands failed: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-17T12:20:18.494-07:00 [telegram] command sync failed: GrammyError: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-17T12:20:18.904-07:00 [telegram] setMyCommands failed: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-17T12:20:18.908-07:00 [telegram] command sync failed: GrammyError: Call to 'setMyCommands' failed! (404: Not Found)
2026-03-17T12:20:32.225-07:00 [telegram] deleteWebhook failed: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-17T12:20:32.231-07:00 [telegram] [chloe] channel exited: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-17T12:20:32.251-07:00 [telegram] deleteMyCommands failed: Call to 'deleteMyCommands' failed! (404: Not Found)
2026-03-17T12:20:32.258-07:00 [telegram] deleteMyCommands failed: Call to 'deleteMyCommands' failed! (404: Not Found)
2026-03-17T12:20:32.264-07:00 [telegram] deleteWebhook failed: Call to 'deleteWebhook' failed! (404: Not Found)
2026-03-17T12:20:32.267-07:00 [telegram] [r