import { handleReadPdfFunc } from './src/handlers/readPdf.ts';
import path from 'path';

async function main() {
  const filePath = 'pdfs/inwi-manual.pdf';

  const result = await handleReadPdfFunc({
    sources: [
      {
        path: filePath
      }
    ],
    include_full_text: true,
    include_metadata: true,
    include_page_count: true
  });

  console.log(JSON.stringify(result, null, 2));
}

main();

