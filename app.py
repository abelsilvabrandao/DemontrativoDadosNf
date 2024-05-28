import os
import json
from flask import Flask, request, render_template, redirect, url_for, send_file
import xml.etree.ElementTree as ET
import pandas as pd

app = Flask(__name__)

UPLOAD_FOLDER = 'C:\\Users\\abel\\Editor de XML\\uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

def parse_xml(xml_str):
    try:
        root = ET.fromstring(xml_str)
        namespace = "http://www.portalfiscal.inf.br/nfe"

        ide = root.find('.//{{{0}}}ide'.format(namespace))
        if ide is None:
            raise ValueError("Elemento 'ide' não encontrado")

        nNF_element = ide.find('.//{{{0}}}nNF'.format(namespace))
        if nNF_element is None:
            raise ValueError("Elemento 'nNF' não encontrado")

        produtos = []
        for produto in root.findall('.//{{{0}}}det'.format(namespace)):
            prod = produto.find('.//{{{0}}}prod'.format(namespace))
            if prod is None:
                raise ValueError("Elemento 'prod' não encontrado")

            cProd_element = prod.find('.//{{{0}}}cProd'.format(namespace))
            xProd_element = prod.find('.//{{{0}}}xProd'.format(namespace))
            CFOP_element = prod.find('.//{{{0}}}CFOP'.format(namespace))
            uCom_element = prod.find('.//{{{0}}}uCom'.format(namespace))
            qCom_element = prod.find('.//{{{0}}}qCom'.format(namespace))
            infAdProd_element = produto.find(
                './/{{{0}}}infAdProd'.format(namespace))

            if None in (
                    cProd_element,
                    xProd_element,
                    CFOP_element,
                    uCom_element,
                    qCom_element):
                raise ValueError(
                    "Um ou mais elementos de produto não encontrados")

            cProd = cProd_element.text
            xProd = xProd_element.text
            CFOP = CFOP_element.text
            uCom = uCom_element.text
            qCom = qCom_element.text
            infAdProd = infAdProd_element.text if infAdProd_element is not None else ''

            produtos.append({'cProd': cProd,
                             'xProd': xProd,
                             'CFOP': CFOP,
                             'uCom': uCom,
                             'qCom': qCom,
                             'infAdProd': infAdProd})

        nNF = nNF_element.text

        return nNF, produtos
    except Exception as e:
        raise ValueError(f"Erro ao analisar o XML: {str(e)}")


@app.route('/generate-excel-report', methods=['POST'])
def generate_excel_report():
    try:
        all_files_data = request.form.get('all_files_data')
        all_files_data = json.loads(all_files_data)

        produtos = []
        for file_data in all_files_data:
            nNF = file_data.get('nNF', '')
            file_produtos = file_data.get('produtos', [])
            for produto in file_produtos:
                produtos.append({
                    'Código Item': produto.get('cProd', ''),
                    'Descrição SKU': produto.get('xProd', ''),
                    'CFOP': produto.get('CFOP', ''),
                    'Unidade de Medida': produto.get('uCom', ''),
                    'Quantidade': int(float(produto.get('qCom', '0'))),
                    'NF Ref. Entrada': produto.get('infAdProd', ''),
                    'NF Retorno/Entrada': nNF
                })

        df = pd.DataFrame(produtos)
        excel_filename = os.path.join(
            app.config['UPLOAD_FOLDER'], 'report.xlsx')
        df.to_excel(excel_filename, index=False)

        return redirect(
            url_for(
                'download_excel_report',
                filename='report.xlsx'))
    except Exception as e:
        return f"Erro ao gerar o relatório Excel: {str(e)}", 500


@app.route('/')
def upload_form():
    return render_template('index.html')


@app.route('/processar-xml', methods=['POST'])
def process_xml():
    try:
        xml_files = request.files.getlist('xml_file')
        if not xml_files:
            return 'Nenhum arquivo selecionado', 400

        all_files_data = []
        for xml_file in xml_files:
            if xml_file.filename == '':
                continue
            xml_str = xml_file.read().decode('utf-8')
            nNF, produtos = parse_xml(xml_str)
            all_files_data.append({'nNF': nNF, 'produtos': produtos})

        return render_template('edit_xml.html', all_files_data=all_files_data)
    except Exception as e:
        return f"Erro ao processar o XML: {str(e)}", 500


@app.route('/download-xml')
def download_xml():
    try:
        filename = request.args.get('filename')
        if filename is None:
            return "Erro: Nome do arquivo não fornecido", 400
        return send_file(
            os.path.join(
                app.config['UPLOAD_FOLDER'],
                filename),
            as_attachment=True)
    except Exception as e:
        return f"Erro ao baixar o arquivo XML: {str(e)}", 500


@app.route('/download-excel-report')
def download_excel_report():
    try:
        filename = request.args.get('filename')
        if filename is None:
            return "Erro: Nome do arquivo não fornecido", 400
        return send_file(
            os.path.join(
                app.config['UPLOAD_FOLDER'],
                filename),
            as_attachment=True)
    except Exception as e:
        return f"Erro ao baixar o arquivo Excel: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True)