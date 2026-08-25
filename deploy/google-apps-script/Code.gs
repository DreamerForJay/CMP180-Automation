/** CMP180 Cloud Viewer — Google Apps Script Web App entry point. */
function doGet() {
  return HtmlService.createTemplateFromFile('Index')
    .evaluate()
    .setTitle('CMP180 Automation — Cloud Viewer')
    .addMetaTag('viewport', 'width=device-width, initial-scale=1');
}

function include(filename) {
  return HtmlService.createHtmlOutputFromFile(filename).getContent();
}

function getApplicationInfo() {
  // 雲端版只能分析去識別化資料；不得在此加入 CMP180 IP、SCPI 或 RF 控制端點。
  return {
    version: '0.1.0',
    mode: 'READ_ONLY',
    updatedAt: new Date().toISOString(),
  };
}
