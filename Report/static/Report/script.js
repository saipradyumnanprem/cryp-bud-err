conslog.log("Works!")
fetch('http://127.0.0.1:8000/history/')
	.then((r) => r.json())
	.then((response) => {
		console.log(response)

		//candleSeries.setData(response);
	})
