fetch("https://api.allorigins.win/get?url=" + encodeURIComponent("https://query2.finance.yahoo.com/v8/finance/chart/CL=F"))
  .then(res => res.json())
  .then(data => console.log("Status:", data.status, "Length:", data.contents.length))
  .catch(err => console.error("Error:", err.message));
