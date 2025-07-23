const puppeteer = require('puppeteer');
(async ()=>{
  const br = await puppeteer.launch();
  const pg = await br.newPage();
  await pg.goto('http://localhost:3000');
  await pg.type('input[id="username"]','attacker',{delay:0});
  await pg.type('input[type="password"]','pw',{delay:0});
  await pg.click('button[type="submit"]');
  await pg.waitForSelector('.attack');
  console.log('Blocked: ', await pg.$eval('.attack', el => el.textContent));
  await br.close();
})();
