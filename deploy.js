const axios = require('axios');

const EMERGENT_API_KEY = process.env.EMERGENT_API_KEY;
const EMERGENT_API_URL = 'https://api.emergent.host';

async function deploy() {
  try {
    console.log('🚀 Starting Thai2Drive deployment...');
    
    const response = await axios.post(`${EMERGENT_API_URL}/deploy`, {
      project: 'thai2drive',
      branch: 'main',
      timestamp: new Date().toISOString()
    }, {
      headers: {
        'Authorization': `Bearer ${EMERGENT_API_KEY}`,
        'Content-Type': 'application/json'
      }
    });
    
    console.log('✅ Deployment successful!');
    console.log('Status:', response.data.status);
    process.exit(0);
  } catch (error) {
    console.error('❌ Deployment failed:', error.message);
    process.exit(1);
  }
}

deploy();