from langchain_core.tools import tool
import xml.etree.ElementTree as ET
import requests

SAT_WS_URL = "https://consultaqr.facturaelectronica.sat.gob.mx/ConsultaCFDIService.svc"

@tool
def validar_cfdi_sat(rfc_emisor: str, rfc_receptor: str, total: str, uuid: str):
    """
    Valida un CFDI directamente contra el SAT usando el Web Service SOAP.
    Args:
        rfc_emisor (str): RFC del emisor
        rfc_receptor (str): RFC del receptor
        total (str): Total del CFDI con 6 decimales
            Ejemplo: 345.300000
        uuid (str): UUID del timbre fiscal
    Returns:
        dict: Resultado de validación SAT
    """
    expresion_impresa = f"?re={rfc_emisor}&rr={rfc_receptor}&tt={total}&id={uuid}"

    soap_body = f"""
    <soapenv:Envelope
        xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
        xmlns:tem="http://tempuri.org/">
        <soapenv:Header/>
        <soapenv:Body>
            <tem:Consulta>
                <tem:expresionImpresa>
                    <![CDATA[{expresion_impresa}]]>
                </tem:expresionImpresa>
            </tem:Consulta>
        </soapenv:Body>
    </soapenv:Envelope>
    """

    headers = {
        "Content-Type": "text/xml; charset=utf-8",
        "SOAPAction": "http://tempuri.org/IConsultaCFDIService/Consulta",
    }

    response = requests.post(
        SAT_WS_URL, data=soap_body.encode("utf-8"), headers=headers, timeout=20
    )
    response.raise_for_status()

    # Parse XML response
    root = ET.fromstring(response.content)
    namespaces = {
        "a": "http://schemas.datacontract.org/2004/07/Sat.Cfdi.Negocio.ConsultaCfdi.Servicio"
    }

    resultado = {
        "codigo_estatus": root.find(".//a:CodigoEstatus", namespaces),
        "estado": root.find(".//a:Estado", namespaces),
        "es_cancelable": root.find(".//a:EsCancelable", namespaces),
        "estatus_cancelacion": root.find(".//a:EstatusCancelacion", namespaces),
    }

    return {
        key: value.text if value is not None else None
        for key, value in resultado.items()
    }
