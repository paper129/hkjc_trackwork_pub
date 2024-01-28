# HKJC Trackwork Data API
A flask based app, using Chromedriver to fetch HKJC Trackwork Page for getting all trackwork details from the page

URL Routing: /api/getTrackwork

Parameters: race (Race No, 1-11), date (Race Date, Format: yyyy/mm/dd), loc (2 digit location code, i.e. ST = Sha Tin, HV = Happy Valley)

```Example for a full URL: https://api.domain.com/api/getTrackwork?race=1&date=2021/01/01&loc=ST```

This API is based on the HKJC Trackwork Page, which is a non-static page. When there is no data, a html response will be returned with the following message:
```
<html>

<head>
	<title>Internal Server Error</title>
</head>

<body>
	<h1>
		<p>Internal Server Error</p>
	</h1>

</body>

</html>
```
Please ensure the parameters are correct before calling the API and the Trackwork Page is available before using.

This repository does not contain Chromedriver 118.0.5982.0.0, please download the correct version from https://chromedriver.chromium.org/downloads and place it in the same folder.

This API is also designed & tested to run on GCP Cloud Run by adding a Dockerfile, please ensure the correct version of Chromedriver is used.

This is a personal project and is not related to HKJC.

This API is not for commercial use, please use it for personal use only.
