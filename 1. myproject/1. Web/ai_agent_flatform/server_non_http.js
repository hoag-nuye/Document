const net = require('net');
const fs = require('fs');

const server = net.createServer((socket) => {
  socket.on('data', (data) => {
    console.log("----------------------------------");
    // console.log("DATA:");
    // console.log(data)
    const request = data.toString();
    // console.log("----------------------------------");
    // console.log("Received request:");
    // // In ra toàn bộ HTTP request nhận được
    console.log(request.split('\r\n')[0]);
    console.log("----------------------------------");
    console.log(`Client IP: ${socket.remoteAddress}`);
    console.log(`Client ephemeral port: ${socket.remotePort}`);
    console.log("============ END =================");

    // Lấy dòng đầu tiên trong HTTP request (VD: GET /?user=a&pass=b HTTP/1.1)
    const requestLine = request.split('\r\n')[0];
     // Tách request line thành method và url
    const [method, url] = requestLine.split(' ');
    const [path, queryString] = url.split('?');
    const query = new URLSearchParams(queryString);

    const user = query.get('user') || 'unknown';
    const pass = query.get('pass') || 'unknown';

    // Body HTML phản hồi
    // const body = 
    //     `<html>
    //       <head>
    //         <title>Waun</title>
    //         <link rel="icon" href="/Waun.png" />
    //       </head>
    //       <body>
    //         <h1>Xin chào! </h1> 
    //         <p>${user}</p>
    //         <p>Pass: ${pass}</p> 
    //       </body>
    //     </html>`;

    // Gui phản hồi cho cac request cua client

    // Khoi tao path cho file HTML va content type cho response
    let filePath = './ui_test/index.html';
    let contentType = 'text/html';

    // Chinh sua filePath va contentType tuong ung voi cac request
    if (url.endsWith('.css')) {
      filePath = `./ui_test${url}`;
      contentType = 'text/css';
    } else if (url.endsWith('.js')) {
      filePath = `./ui_test${url}`;
      contentType = 'application/javascript';
    }

    // Doc noi dung file tuong ung
    fs.readFile(filePath, (err, body) => {
      if (err) {
        console.error('Error reading file:', err);
        socket.write('HTTP/1.1 404 Not Found\r\n\r\n');
        socket.end();
        return;
      }

      // Tạo phản hồi HTTP
      const response =
        'HTTP/1.1 200 OK\r\n' +
        `Content-Type: ${contentType}\r\n` +
        `Content-Length: ${Buffer.byteLength(body)}\r\n` +
        '\r\n' +
        body;

      // Gửi phản hồi về client
      socket.write(response);
      socket.end();
    })

  });
});

server.listen(8080, () => {
  console.log('TCP HTTP-like server listening on port 8080');
});
