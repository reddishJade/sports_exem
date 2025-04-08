import { saveAs } from 'file-saver'
import * as XLSX from 'xlsx'
import { jsPDF } from 'jspdf'
import 'jspdf-autotable'
import html2canvas from 'html2canvas'

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
