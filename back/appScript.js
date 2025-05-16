function enviarDatosHeartRateAWS() {
  const heartRateData = obtenerUltimasMedicionesHeartRate();
  
  if (!heartRateData || heartRateData.length === 0) {
    Logger.log("No hay datos de frecuencia cardíaca para enviar");
    return;
  }

  const awsApiUrl = "https://z7pl9c79n3.execute-api.us-east-1.amazonaws.com/prod/heartrate";
  
  heartRateData.forEach((medicion, index) => {
    const unixTimestamp = Math.floor(medicion.timestamp.getTime() / 1000);
    
    const payload = JSON.stringify({
      deviceId: "003",
      heartRate: medicion.bpm,
      timestamp: unixTimestamp 
    });
    
    const options = {
      method: "POST",
      contentType: "application/json",
      payload: payload,
      muteHttpExceptions: true
    };
    
    try {
      Logger.log(`Enviando medición ${index + 1}: ${medicion.bpm} bpm`);
      const response = UrlFetchApp.fetch(awsApiUrl, options);
      Logger.log("Respuesta de AWS: " + response.getContentText());
    } catch (e) {
      Logger.log("Error al enviar: " + e.toString());
    }
  });
}

function obtenerUltimasMedicionesHeartRate() {
  const now = Date.now() * 1000000; 
  const start = now - 1 * 60 * 60 * 1000000000; 
  const datasetId = start + "-" + now;

  const headers = {
    Authorization: "Bearer " + ScriptApp.getOAuthToken()
  };

  const fuentesUrl = "https://www.googleapis.com/fitness/v1/users/me/dataSources";
  const response = UrlFetchApp.fetch(fuentesUrl, { headers: headers });
  const dataSources = JSON.parse(response.getContentText()).dataSource;

  const fuentesFrecuencia = dataSources.filter(ds => ds.dataType.name === "com.google.heart_rate.bpm");

  if (fuentesFrecuencia.length === 0) {
    Logger.log("No hay fuentes de datos de frecuencia cardíaca");
    return [];   
  }

  const mediciones = [];

  for (const fuente of fuentesFrecuencia) {
    const dataStreamId = fuente.dataStreamId;
    const url = "https://www.googleapis.com/fitness/v1/users/me/dataSources/" +
                encodeURIComponent(dataStreamId) + "/datasets/" + datasetId;

    try {
      const dataResp = UrlFetchApp.fetch(url, { headers: headers });
      const json = JSON.parse(dataResp.getContentText());
      const points = json.point || [];

      points.forEach((point) => {
        const timestamp = new Date(Number(point.startTimeNanos) / 1e6);
        const bpm = point.value[0].fpVal;
        
        mediciones.push({
          bpm: bpm,
          timestamp: timestamp,
          fuente: dataStreamId
        });
      });
      
    } catch (e) {
      Logger.log("Error al consultar fuente " + dataStreamId + ": " + e.message);
    }
  }

  mediciones.sort((a, b) => b.timestamp - a.timestamp);
  
  Logger.log("Se encontraron " + mediciones.length + " mediciones de frecuencia cardíaca");
  return mediciones;
}