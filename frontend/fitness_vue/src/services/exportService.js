import { saveAs } from 'file-saver'
import * as XLSX from 'xlsx'
import { jsPDF } from 'jspdf'
import 'jspdf-autotable'
import html2canvas from 'html2canvas'
import { marked } from 'marked'

/**
 * 导出数据为Excel文件
 * @param {Object[]} data 要导出的数据
 * @param {string} fileName 文件名
 * @param {string} sheetName 工作表名称
 */
export const exportToExcel = (data, fileName, sheetName = 'Sheet1') => {
  const worksheet = XLSX.utils.json_to_sheet(data)
  const workbook = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(workbook, worksheet, sheetName)
  
  // 生成Excel文件
  const excelBuffer = XLSX.write(workbook, { bookType: 'xlsx', type: 'array' })
  const fileData = new Blob([excelBuffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
  
  // 保存文件
  saveAs(fileData, `${fileName}.xlsx`)
}

/**
 * 导出表格数据为PDF文件
 * @param {Object[]} data 表格数据
 * @param {Object[]} columns 表格列定义
 * @param {string} title 标题
 * @param {string} fileName 文件名
 */
export const exportTableToPdf = (data, columns, title, fileName) => {
  const doc = new jsPDF()
  
  // 添加标题
  doc.setFontSize(18)
  doc.text(title, 14, 22)
  
  // 生成日期
  doc.setFontSize(10)
  doc.text(`导出日期: ${new Date().toLocaleDateString()}`, 14, 30)
  
  // 准备表格数据
  const tableHeaders = columns.map(col => col.title)
  const tableData = data.map(item => columns.map(col => item[col.dataIndex]))
  
  // 添加表格
  doc.autoTable({
    head: [tableHeaders],
    body: tableData,
    startY: 35,
    styles: { fontSize: 10, cellPadding: 3 },
    headStyles: { fillColor: [41, 128, 185], textColor: 255 }
  })
  
  // 保存文件
  doc.save(`${fileName}.pdf`)
}

/**
 * 将DOM元素导出为PDF
 * @param {HTMLElement} element DOM元素
 * @param {string} fileName 文件名
 */
export const exportElementToPdf = async (element, fileName) => {
  const canvas = await html2canvas(element, {
    scale: 2, // 提高清晰度
    useCORS: true, // 允许加载跨域图片
    logging: false
  })
  
  const imgData = canvas.toDataURL('image/png')
  const pdf = new jsPDF({
    orientation: 'portrait',
    unit: 'mm',
    format: 'a4'
  })
  
  const pdfWidth = pdf.internal.pageSize.getWidth()
  const pdfHeight = pdf.internal.pageSize.getHeight()
  const imgWidth = canvas.width
  const imgHeight = canvas.height
  const ratio = Math.min(pdfWidth / imgWidth, pdfHeight / imgHeight)
  const imgX = (pdfWidth - imgWidth * ratio) / 2
  const imgY = 30
  
  // 添加标题
  pdf.setFontSize(16)
  pdf.text(fileName, pdfWidth / 2, 15, { align: 'center' })
  
  // 添加图片
  pdf.addImage(imgData, 'PNG', imgX, imgY, imgWidth * ratio, imgHeight * ratio)
  
  // 保存文件
  pdf.save(`${fileName}.pdf`)
}

/**
 * 打印DOM元素
 * @param {HTMLElement} element DOM元素
 */
export const printElement = (element) => {
  const printWindow = window.open('', '_blank')
  const printDocument = printWindow.document
  
  // 添加打印样式
  printDocument.write(`
    <html>
      <head>
        <title>打印</title>
        <style>
          body {
            font-family: Arial, sans-serif;
            padding: 20px;
          }
          table {
            border-collapse: collapse;
            width: 100%;
          }
          th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
          }
          th {
            background-color: #f2f2f2;
          }
          @media print {
            button {
              display: none;
            }
          }
        </style>
      </head>
      <body>
        ${element.innerHTML}
        <button onclick="window.print();window.close();" style="margin-top: 20px; padding: 10px;">打印</button>
      </body>
    </html>
  `)
  
  printDocument.close()
}

/**
 * 导出聊天对话为文本文件
 * @param {Object[]} messages 聊天消息数组
 * @param {string} title 对话标题
 */
export const exportChatAsText = (messages, title) => {
  let content = `对话: ${title}\n`
  content += `导出时间: ${new Date().toLocaleString()}\n\n`
  
  messages.forEach(msg => {
    const role = msg.role === 'user' ? '用户' : 'AI助手'
    content += `${role} (${new Date(msg.timestamp).toLocaleString()}):\n${msg.content}\n\n`
  })
  
  const blob = new Blob([content], { type: 'text/plain;charset=utf-8' })
  saveAs(blob, `对话-${title}.txt`)
}

/**
 * 导出聊天对话为Markdown文件
 * @param {Object[]} messages 聊天消息数组
 * @param {string} title 对话标题
 */
export const exportChatAsMarkdown = (messages, title) => {
  let content = `# 对话: ${title}\n\n`
  content += `*导出时间: ${new Date().toLocaleString()}*\n\n`
  
  messages.forEach(msg => {
    const role = msg.role === 'user' ? '## 用户' : '## AI助手'
    content += `${role}\n\n${msg.content}\n\n*时间: ${new Date(msg.timestamp).toLocaleString()}*\n\n---\n\n`
  })
  
  const blob = new Blob([content], { type: 'text/markdown;charset=utf-8' })
  saveAs(blob, `对话-${title}.md`)
}

/**
 * 导出聊天对话为HTML文件
 * @param {Object[]} messages 聊天消息数组
 * @param {string} title 对话标题
 */
export const exportChatAsHTML = (messages, title) => {
  let content = `<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>对话: ${title}</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      max-width: 800px;
      margin: 0 auto;
      padding: 20px;
      line-height: 1.6;
    }
    h1 {
      color: #333;
      border-bottom: 1px solid #eee;
      padding-bottom: 10px;
    }
    .message {
      margin-bottom: 20px;
      padding: 15px;
      border-radius: 8px;
    }
    .user {
      background-color: #f0f0f0;
    }
    .assistant {
      background-color: #e6f7f3;
    }
    .role {
      font-weight: bold;
      margin-bottom: 5px;
    }
    .timestamp {
      font-size: 0.8em;
      color: #777;
      margin-top: 5px;
    }
    pre {
      background-color: #f6f8fa;
      padding: 10px;
      border-radius: 5px;
      overflow-x: auto;
    }
    code {
      font-family: monospace;
      background-color: rgba(0,0,0,0.05);
      padding: 2px 4px;
      border-radius: 3px;
    }
  </style>
</head>
<body>
  <h1>对话: ${title}</h1>
  <p><em>导出时间: ${new Date().toLocaleString()}</em></p>
  <div class="chat-content">
`

  messages.forEach(msg => {
    const role = msg.role === 'user' ? '用户' : 'AI助手'
    const cssClass = msg.role === 'user' ? 'user' : 'assistant'
    const formattedContent = msg.role === 'assistant' ? marked(msg.content) : msg.content.replace(/\n/g, '<br>')
    
    content += `    <div class="message ${cssClass}">
      <div class="role">${role}</div>
      <div class="content">${formattedContent}</div>
      <div class="timestamp">${new Date(msg.timestamp).toLocaleString()}</div>
    </div>
`
  })

  content += `  </div>
</body>
</html>`

  const blob = new Blob([content], { type: 'text/html;charset=utf-8' })
  saveAs(blob, `对话-${title}.html`)
}
