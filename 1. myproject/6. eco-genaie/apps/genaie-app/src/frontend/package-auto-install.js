const { execSync } = require('child_process');

console.log('🔍 Đang kiểm tra missing dependencies bằng depcheck...');

let output;

try {
  // Nếu mọi thứ OK, lấy được output
  output = execSync('npx depcheck --json', { encoding: 'utf-8' });
} catch (error) {
  // Nếu bị lỗi do exit code 1, vẫn lấy stdout ra (vì depcheck vẫn ghi JSON ra stdout)
  if (error.stdout) {
    output = error.stdout.toString();
  } else {
    console.error('❌ depcheck gặp lỗi không xác định:', error.message);
    process.exit(1);
  }
}

try {
  const result = JSON.parse(output);
  const missing = result.missing || {};
  const missingDeps = Object.keys(missing);

  if (missingDeps.length === 0) {
    console.log('✅ Không có dependency nào bị thiếu!');
  } else {
    console.log('⚠️  Các package bị thiếu:', missingDeps.join(', '));
    const installCmd = 'npm install ' + missingDeps.join(' ');
    console.log('📦 Đang cài đặt:', installCmd);
    execSync(installCmd, { stdio: 'inherit' });
    console.log('✅ Cài đặt hoàn tất!');
  }

  process.exit(0); // Luôn exit 0
} catch (err) {
  console.error('❌ Không thể phân tích output JSON từ depcheck:', err.message);
  process.exit(1);
}
