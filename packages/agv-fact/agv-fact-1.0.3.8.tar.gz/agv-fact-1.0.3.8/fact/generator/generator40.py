# -*- encoding: utf-8 -*-

from Crypto.Hash import SHA256

from .contants import TRASLADO, EGRESO, INGRESO, PAGO, COMPLEMENTO_CARTA_PORTE, COMPLEMENTO_PAGOS, ST_RECIBO_DONATIVO, \
    COMPLEMENTO_DONATARIAS
from .generator_abstract import AbstractGeneratorXml
from .utils import replace


class GeneratorXmlFourDotZero(AbstractGeneratorXml):

    def __init__(self, data):
        super(self.__class__, self).__init__(data)
        self.version = '4.0'
        self.algoritmoSha = SHA256
        self.__cadena_original = ''
        if self.data:
            self.impuestos_trasladados = self.data.get('impuestos_trasladados', [])
            self.impuestos_retenidos = self.data.get('impuestos_retenidos', [])

    def generate_xml(self):
        self.reset_dom()
        dom = self.dom.childNodes[0]
        dom.setAttribute('xmlns:cfdi', 'http://www.sat.gob.mx/cfd/4')
        if self.tipo_comprobante == INGRESO and self.data.get('subtipo') == ST_RECIBO_DONATIVO: #recibo donativo
            dom.setAttribute('xsi:schemaLocation',
                             'http://www.sat.gob.mx/cfd/4 ' +
                             'http://www.sat.gob.mx/sitio_internet/cfd/4/cfdv40.xsd ' +
                             'http://www.sat.gob.mx/donat ' +
                             'http://www.sat.gob.mx/sitio_internet/cfd/donat/donat11.xsd')
            dom.setAttribute('xmlns:donat', 'http://www.sat.gob.mx/donat')
        elif self.tipo_comprobante == PAGO:
            dom.setAttribute('xmlns:pago20', 'http://www.sat.gob.mx/Pagos20')
            dom.setAttribute('xsi:schemaLocation',
                             'http://www.sat.gob.mx/cfd/4 ' +
                             'http://www.sat.gob.mx/sitio_internet/cfd/4/cfdv40.xsd ' +
                             'http://www.sat.gob.mx/Pagos20 ' +
                             'http://www.sat.gob.mx/sitio_internet/cfd/Pagos/Pagos20.xsd')
        elif self.complemento == COMPLEMENTO_CARTA_PORTE:
            cartaporte_data = self.data.get('complemento_cartaporte', {})
            dom.setAttribute('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
            if cartaporte_data.get('Version') == '3.1':
                dom.setAttribute('xmlns:cartaporte31', 'http://www.sat.gob.mx/CartaPorte31')
                dom.setAttribute('xsi:schemaLocation',
                                 'http://www.sat.gob.mx/cfd/4 ' +
                                 'http://www.sat.gob.mx/sitio_internet/cfd/4/cfdv40.xsd ' +
                                 'http://www.sat.gob.mx/CartaPorte31 ' +
                                 'http://www.sat.gob.mx/sitio_internet/cfd/CartaPorte/CartaPorte31.xsd')
            elif cartaporte_data.get('Version') == '3.0':
                dom.setAttribute('xmlns:cartaporte30', 'http://www.sat.gob.mx/CartaPorte30')
                dom.setAttribute('xsi:schemaLocation',
                                 'http://www.sat.gob.mx/cfd/4 ' +
                                 'http://www.sat.gob.mx/sitio_internet/cfd/4/cfdv40.xsd ' +
                                 'http://www.sat.gob.mx/CartaPorte30 ' +
                                 'http://www.sat.gob.mx/sitio_internet/cfd/CartaPorte/CartaPorte30.xsd')
            else:
                dom.setAttribute('xmlns:cartaporte20', 'http://www.sat.gob.mx/CartaPorte20')
                dom.setAttribute('xsi:schemaLocation',
                                 'http://www.sat.gob.mx/cfd/4 ' +
                                 'http://www.sat.gob.mx/sitio_internet/cfd/4/cfdv40.xsd ' +
                                 'http://www.sat.gob.mx/CartaPorte20 ' +
                                 'http://www.sat.gob.mx/sitio_internet/cfd/CartaPorte/CartaPorte20.xsd')
        else:
            dom.setAttribute('xsi:schemaLocation', 'http://www.sat.gob.mx/cfd/4 http://www.sat.gob.mx/sitio_internet/cfd/4/cfdv40.xsd')
            dom.setAttribute('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')


        dom.setAttribute('Version', self.data.get('version', ''))
        dom.setAttribute('Serie', self.data.get('serie', ''))
        dom.setAttribute('Folio', self.data.get('folio', ''))
        dom.setAttribute('Fecha', self.data.get('fecha'))
        dom.setAttribute('Sello', '')
        dom.setAttribute('NoCertificado', self.data.get('no_certificado'))
        dom.setAttribute('Certificado', self.data.get('certificado'))
        dom.setAttribute('TipoDeComprobante', self.tipo_comprobante)
        dom.setAttribute('LugarExpedicion', self.data.get('lugar_expedicion', ''))
        dom.setAttribute('Exportacion', self.data.get('exportacion', '01'))

        if self.data.get('confirmacion'):
            dom.setAttribute('Confirmacion', self.data.get('confirmacion'))  # opcional

        # <cfdi:InformacionGlobal Periodicidad="01" Meses="01" Año="2021"/>
        if self.data.get('factura_global') == 'SI':
            dom.appendChild(self.get_informacion_global())

        if len(self.data.get('cfdi_relacionados', [])) > 0:
            if self.data.get('tipo_relacion', '') == '':
                raise Exception('Debe especificar el tipo de relación de los documentos')
            dom.appendChild(self.get_cfdi_relacionados(self.data.get('cfdi_relacionados', [])))

        dom.appendChild(self.get_emisor())
        dom.appendChild(self.get_receptor())

        conceptos_list = self.data.get('conceptos', [])

        if self.tipo_comprobante == INGRESO or self.tipo_comprobante == EGRESO and not self.data.get('concepto_fijo'):
            dom.setAttribute('FormaPago', self.data.get('forma_pago'))

            if self.data.get('condiciones_pago'):
                dom.setAttribute('CondicionesDePago', self.data.get('condiciones_pago'))

            if self.data.get('descuento') and self.data.get('descuento') not in ['0', '0.00', '0.000000']:
                dom.setAttribute('Descuento', self.data.get('descuento'))

            dom.setAttribute('MetodoPago', self.data.get('metodo_pago'))
            dom.setAttribute('Moneda', self.data.get('moneda'))
            dom.setAttribute('TipoCambio', '1' if self.data.get('moneda') == 'MXN' else self.data.get('tipo_cambio'))
            dom.setAttribute('SubTotal', self.data.get('subtotal', ''))
            dom.setAttribute('Total', self.data.get('total', ''))
            conceptos_list = self.data.get('conceptos', [])
            if len(conceptos_list) > 0:
                dom.appendChild(self.get_conceptos(conceptos_list))
            if len(self.impuestos_trasladados) > 0 or len(self.impuestos_retenidos) > 0:
                dom.appendChild(self.get_impuestos())
        elif self.tipo_comprobante == PAGO:
            dom.setAttribute('SubTotal','0')
            dom.setAttribute('Moneda','XXX')
            dom.setAttribute('Total','0')
            dom.appendChild(self.get_concepto_fijo())
        elif self.tipo_comprobante == EGRESO and self.data.get('concepto_fijo'):
            dom.setAttribute('FormaPago',self.data.get('forma_pago'))

            if self.data.get('condiciones_pago'):
                dom.setAttribute('CondicionesDePago', self.data.get('condiciones_pago'))

            dom.setAttribute('MetodoPago', self.data.get('metodo_pago'))
            dom.setAttribute('Moneda', self.data.get('moneda'))  # 'Peso Mexicano'
            # 'Opcional solo cuando moneda es distinta de MXN'
            dom.setAttribute('TipoCambio', '1' if self.data.get('moneda') == 'MXN' else self.data.get('tipo_cambio'))
            dom.setAttribute('SubTotal', str(self.data.get('subtotal')))
            dom.setAttribute('Total', str(self.data.get('total')))
            dom.appendChild(self.get_concepto_fijo())
            if bool(self.data.get('aplica_retencion', False)) or bool(self.data.get('aplica_traslado', False)):
                dom.appendChild(self.get_impuestos())
        elif self.tipo_comprobante == TRASLADO:
            dom.setAttribute('SubTotal','0')
            dom.setAttribute('Moneda','XXX')
            dom.setAttribute('Total','0')
            if len(conceptos_list) > 0:
                dom.appendChild(self.get_conceptos(conceptos_list))
        if self.complemento in [COMPLEMENTO_DONATARIAS, COMPLEMENTO_PAGOS, COMPLEMENTO_CARTA_PORTE]:
            dom.appendChild(self.get_complementos())
        self.dom = dom
        return self.dom

    def get_cfdi_relacionados(self, cfdirelacionados):
        try:
            relacionados = self.dom.createElement('cfdi:CfdiRelacionados')
            relacionados.setAttribute('TipoRelacion', self.data.get('tipo_relacion'))
            for uuid_cfdi in cfdirelacionados:
                relacionado = self.dom.createElement('cfdi:CfdiRelacionado')
                relacionado.setAttribute('UUID', uuid_cfdi)
                relacionados.appendChild(relacionado)
            return relacionados
        except Exception as e:
            raise Exception("Ocurrio un error al agregar los cfdis relacionados. Error::: " + str(e))

    def get_informacion_global(self):
        try:
            informacion_global = self.dom.createElement('cfdi:InformacionGlobal')
            informacion_global.setAttribute('Periodicidad', self.data.get('periodicidad'))
            informacion_global.setAttribute('Meses', self.data.get('meses'))
            informacion_global.setAttribute('Año', self.data.get('año'))
            return informacion_global
        except Exception as e:
            raise Exception("Ocurrio un error al agregar la información global. Error::: " + str(e))

    def get_emisor(self):
        try:
            emisor = self.dom.createElement('cfdi:Emisor')
            emisor.setAttribute('Rfc', self.data.get('emisor_rfc'))
            emisor.setAttribute('Nombre', replace(self.data.get('emisor_nombre', '')).strip())
            emisor.setAttribute('RegimenFiscal', self.data.get('regimen_fiscal'))
            return emisor
        except Exception as e:
            raise Exception("Ocurrio un error al agregar al emisor. Error::: " + str(e))

    def get_receptor(self):
        try:
            receptor = self.dom.createElement('cfdi:Receptor')
            receptor.setAttribute('Rfc', self.data.get('receptor_rfc'))
            receptor.setAttribute('Nombre', replace(self.data.get('receptor_nombre', '')).strip())
            receptor.setAttribute('DomicilioFiscalReceptor', self.data.get('domicilio_fiscal_receptor', ''))
            if self.data.get('receptor_residencia_fiscal') != 'MEX':
                receptor.setAttribute('ResidenciaFiscal', self.data.get('receptor_residencia_fiscal'))
                receptor.setAttribute('NumRegIdTrib', self.data.get('receptor_num_reg_id_trib'))
            if self.tipo_comprobante == TRASLADO and self.data.get('uso_cfdi') != 'S01':
                raise Exception('El campo Uso CFDI debe contener el valor S01 - Sin efectos fiscales.')
            receptor.setAttribute('RegimenFiscalReceptor', self.data.get('regimen_fiscal_receptor'))
            receptor.setAttribute('UsoCFDI', self.data.get('uso_cfdi'))
            return receptor
        except Exception as e:
            raise Exception("Ocurrio un error al agregar el receptor. Error::: " + str(e))

    def get_concepto_fijo(self):
        try:
            conceptos = self.dom.createElement('cfdi:Conceptos')
            concepto = self.dom.createElement('cfdi:Concepto')
            concepto.setAttribute('ClaveProdServ','84111506')
            concepto.setAttribute('Cantidad','1')
            concepto.setAttribute('ClaveUnidad','ACT')
            if self.tipo_comprobante == PAGO:
                concepto.setAttribute('Descripcion','Pago')
                concepto.setAttribute('ValorUnitario','0')
                concepto.setAttribute('Importe','0')
                concepto.setAttribute('ObjetoImp', '01')
            elif self.tipo_comprobante == EGRESO:
                if self.data.get('descripcion', '') != '':
                    concepto.setAttribute('Descripcion',replace(self.data.get('descripcion', '').strip()))
                else:
                    raise Exception('Se debe especificar una descripción para poder timbrar')
                concepto.setAttribute('ValorUnitario',str(self.data.get('total')))
                concepto.setAttribute('Importe',str(self.data.get('total')))
                concepto.setAttribute('ObjetoImp', '01')
            conceptos.appendChild(concepto)
            return conceptos
        except Exception as e:
            raise Exception("Ocurrio un error al agregar el conceptoF. Error::: " + str(e))

    def get_impuestos(self):
        try:
            impuestos = self.dom.createElement('cfdi:Impuestos')

            if len(self.impuestos_retenidos) > 0:
                retenciones = self.dom.createElement('cfdi:Retenciones')
                total_retenciones = 0
                for retencion in self.impuestos_retenidos:
                    total_retenciones += float(retencion.get('importe', 0))
                    retenciones.appendChild(self.get_retenciones(retencion))
                impuestos.appendChild(retenciones)
                impuestos.setAttribute('TotalImpuestosRetenidos', str(total_retenciones))

            if len(self.impuestos_trasladados) > 0:
                traslados = self.dom.createElement('cfdi:Traslados')
                total_traslados = 0
                for traslado in self.impuestos_trasladados:
                    total_traslados += float(traslado.get('importe', 0))
                    traslados.appendChild(self.get_traslados(traslado))
                impuestos.appendChild(traslados)
                impuestos.setAttribute('TotalImpuestosTrasladados', str(total_traslados))

            return impuestos
        except Exception as e:
            raise Exception("Ocurrio un error al agregar los impuestos globales. Error::: " + str(e))

    def get_traslados(self, traslado_data):
        traslado = self.dom.createElement('cfdi:Traslado')
        traslado.setAttribute('Base', str(traslado_data.get('base')))
        traslado.setAttribute('Impuesto', traslado_data.get('impuesto'))
        traslado.setAttribute('TipoFactor', traslado_data.get('tipo_factor'))
        if traslado_data.get('tasa_cuota'):
            traslado.setAttribute('TasaOCuota', str(traslado_data.get('tasa_cuota')))
        if traslado_data.get('importe'):
            traslado.setAttribute('Importe', str(traslado_data.get('importe')))
        return traslado

    def get_retenciones(self, retencion_data):
        retencion = self.dom.createElement('cfdi:Retencion')
        retencion.setAttribute('Impuesto', retencion_data.get('impuesto'))
        retencion.setAttribute('Importe', str(retencion_data.get('importe')))
        return retencion

    def get_complementos(self):
        try:
            complemento = self.dom.createElement('cfdi:Complemento')
            if self.complemento == COMPLEMENTO_DONATARIAS:
                complemento.appendChild(self.get_complemento_donatarias())
            elif self.complemento == COMPLEMENTO_PAGOS:
                complemento.appendChild(self.get_complemento_pagos())
            elif self.complemento == COMPLEMENTO_CARTA_PORTE:
                cartaporte_data = self.data.get('complemento_cartaporte', {})
                if cartaporte_data and cartaporte_data.get('Version') == '3.1':
                    complemento.appendChild(self.get_complemento_cartaporte31())
                elif cartaporte_data and cartaporte_data.get('Version') == '3.0':
                    complemento.appendChild(self.get_complemento_cartaporte30())
                else:
                    complemento.appendChild(self.get_complemento_cartaporte20())
            return complemento
        except Exception as e:
            raise Exception("Ocurrio un error al agregar los complementos. Error::: " + str(e))

    def get_complemento_donatarias(self):
        try:
            donataria = self.dom.createElement('donat:Donatarias')
            donataria.setAttribute('xmlns:donat', 'http://www.sat.gob.mx/donat')
            donataria.setAttribute('xsi:schemaLocation',
                                   'http://www.sat.gob.mx/cfd/4 ' +
                                   'http://www.sat.gob.mx/sitio_internet/cfd/4/cfdv40.xsd ' +
                                   'http://www.sat.gob.mx/donat ' +
                                   'http://www.sat.gob.mx/sitio_internet/cfd/donat/donat11.xsd')
            donataria.setAttribute('version', '1.1')
            donataria.setAttribute('noAutorizacion', self.data.get('donataria_no_autorizacion'))
            donataria.setAttribute('fechaAutorizacion', self.data.get('donataria_fecha_autorizacion'))
            donataria.setAttribute('leyenda', self.data.get('leyenda'))
            return donataria
        except Exception as e:
            raise Exception("Ocurrio un error al agregar el complemento de Donatarias. Error::: " + str(e))

    def get_complemento_pagos(self):
        try:
            complemento_data = self.data.get('complemento_pago')
            pagos = self.dom.createElement('pago20:Pagos')
            pagos.setAttribute('Version', complemento_data.get('version'))

            totales_pago = self.get_totales_pago(complemento_data)

            pago = self.dom.createElement('pago20:Pago')
            pago.setAttribute('FechaPago', complemento_data.get('fecha_pago'))

            if complemento_data.get('forma_pago') == '99':
                raise Exception('La forma de pago no puede ser "Por Definir".')

            pago.setAttribute('FormaDePagoP', complemento_data.get('forma_pago'))
            pago.setAttribute('MonedaP', complemento_data.get('moneda'))
            pago.setAttribute('TipoCambioP', complemento_data.get('tipo_cambio'))
            pago.setAttribute('Monto', str(complemento_data.get('monto')))

            if complemento_data.get('numero_operacion'):
                pago.setAttribute('NumOperacion', complemento_data.get('numero_operacion'))

            if complemento_data.get('bancarizado'):
                if complemento_data.get('patron_cuenta_ordenante') and complemento_data.get('patron_cuenta_ordenante') != '':
                    if complemento_data.get('banco_ordenante'):
                        pago.setAttribute('RfcEmisorCtaOrd', complemento_data.get('emisor_cuenta_ordenante_rfc'))
                        if complemento_data.get('emisor_cuenta_ordenante_rfc') == 'XEXX010101000':
                            pago.setAttribute('NomBancoOrdExt', complemento_data.get('emisor_cuenta_ordenante_nombre'))
                    pago.setAttribute('CtaOrdenante', complemento_data.get('emisor_cuenta_ordenante'))
                if complemento_data.get('forma_pago') != '06':
                    if complemento_data.get('emisor_cuenta_beneficiaria_rfc'):
                        pago.setAttribute('RfcEmisorCtaBen', complemento_data.get('emisor_cuenta_beneficiaria_rfc'))
                    pago.setAttribute('CtaBeneficiario', complemento_data.get('emisor_cuenta_beneficiaria'))

            doctos = complemento_data.get('doctos_relacionados', [])
            for docto_relacionado in doctos:
                docto = self.dom.createElement('pago20:DoctoRelacionado')
                docto.setAttribute('IdDocumento', docto_relacionado.get('uuid'))
                docto.setAttribute('Serie', docto_relacionado.get('serie'))
                docto.setAttribute('Folio', docto_relacionado.get('folio'))
                docto.setAttribute('MonedaDR', docto_relacionado.get('moneda'))
                docto.setAttribute('EquivalenciaDR', docto_relacionado.get('equivalencia'))
                docto.setAttribute('NumParcialidad', str(docto_relacionado.get('parcialidad')))
                docto.setAttribute('ImpSaldoAnt', str(docto_relacionado.get('imp_saldo_ant')))
                docto.setAttribute('ImpPagado', str(docto_relacionado.get('imp_pagado')))
                docto.setAttribute('ImpSaldoInsoluto', str(docto_relacionado.get('imp_saldo_insoluto')))
                docto.setAttribute('ObjetoImpDR', docto_relacionado.get('objeto_impuesto', '01'))

                if docto_relacionado.get('objeto_impuesto', '01') != '01':
                    docto.appendChild(self.get_impuestos_documentos_relacionados_pago(docto_relacionado))
                pago.appendChild(docto)
            pagos.appendChild(totales_pago)
            pagos.appendChild(pago)
            if len(complemento_data.get('impuestos_retenidos', [])) > 0 or len(complemento_data.get('impuestos_trasladados', [])):
                pago.appendChild(self.get_impuestos_pago(complemento_data))
            pagos.appendChild(pago)
            return pagos
        except Exception as e:
            raise Exception("Ocurrio un error al agregar el complemento de pago. Error::: " + str(e))

    def get_totales_pago(self, complemento_data):
        totales = self.dom.createElement('pago20:Totales')

        if complemento_data.get('total_retenciones_iva'):
            totales.setAttribute('TotalRetencionesIVA', str(complemento_data.get('total_retenciones_iva')))
        if complemento_data.get('total_retenciones_isr'):
            totales.setAttribute('TotalRetencionesISR', str(complemento_data.get('total_retenciones_isr')))
        if complemento_data.get('total_retenciones_ieps'):
            totales.setAttribute('TotalRetencionesIEPS', str(complemento_data.get('total_retenciones_ieps')))
        if complemento_data.get('total_traslados_base_iva16'):
            totales.setAttribute('TotalTrasladosBaseIVA16', str(complemento_data.get('total_traslados_base_iva16')))
        if complemento_data.get('total_traslados_impuesto_iva16'):
            totales.setAttribute('TotalTrasladosImpuestoIVA16', str(complemento_data.get('total_traslados_impuesto_iva16')))
        if complemento_data.get('total_traslados_base_iva8'):
            totales.setAttribute('TotalTrasladosBaseIVA8', str(complemento_data.get('total_traslados_base_iva8')))
        if complemento_data.get('total_traslados_impuesto_iva8'):
            totales.setAttribute('TotalTrasladosImpuestoIVA8', str(complemento_data.get('total_traslados_impuesto_iva8')))
        if complemento_data.get('total_traslados_base_iva0'):
            totales.setAttribute('TotalTrasladosBaseIVA0', str(complemento_data.get('total_traslados_base_iva0')))
        if complemento_data.get('total_traslados_impuesto_iva0'):
            totales.setAttribute('TotalTrasladosImpuestoIVA0', str(complemento_data.get('total_traslados_impuesto_iva0')))
        if complemento_data.get('total_traslados_base_iva_exento'):
            totales.setAttribute('TotalTrasladosBaseIVAExento', str(complemento_data.get('total_traslados_base_iva_exento')))

        totales.setAttribute('MontoTotalPagos', str(complemento_data.get('monto')))

        return totales

    # ***** Impuestos Pago *****
    def get_impuestos_documentos_relacionados_pago(self, docto_relacionado):
        impuestos = self.dom.createElement('pago20:ImpuestosDR')
        if len(docto_relacionado.get('impuestos_retenidos', [])) > 0:
            retenciones = self.dom.createElement('pago20:RetencionesDR')
            for retencion in docto_relacionado.get('impuestos_retenidos', []):
                retenciones.appendChild(self.get_retenciones_documentos_relacionados(retencion))
            impuestos.appendChild(retenciones)

        if len(docto_relacionado.get('impuestos_trasladados', [])) > 0:
            traslados = self.dom.createElement('pago20:TrasladosDR')
            for traslado in docto_relacionado.get('impuestos_trasladados', []):
                traslados.appendChild(self.get_traslados_documentos_relacionados(traslado))
            impuestos.appendChild(traslados)
        return impuestos

    def get_retenciones_documentos_relacionados(self, retencion_data):
        retencion = self.dom.createElement('pago20:RetencionDR')
        retencion.setAttribute('BaseDR', str(retencion_data.get('base')))  # Importe del documentos_relacionados
        retencion.setAttribute('ImpuestoDR', retencion_data.get('impuesto'))
        retencion.setAttribute('TipoFactorDR', retencion_data.get('tipo_factor', 'Tasa'))  # Tipo factor Tasa ó Cuota
        retencion.setAttribute('TasaOCuotaDR', str(retencion_data.get('tasa_cuota')))  # valor del impuesto que se envia
        retencion.setAttribute('ImporteDR', str(retencion_data.get('importe')))
        return retencion

    def get_traslados_documentos_relacionados(self, traslado_data):
        traslado = self.dom.createElement('pago20:TrasladoDR')
        traslado.setAttribute('BaseDR', str(traslado_data.get('base')))  # Importe del documentos_relacionados
        traslado.setAttribute('ImpuestoDR', traslado_data.get('impuesto', ''))
        traslado.setAttribute('TipoFactorDR', traslado_data.get('tipo_factor', 'Tasa'))  # Tipo factor Tasa ó Cuota
        if traslado_data.get('tipo_factor') in ['Tasa', 'Cuota']:
            traslado.setAttribute('TasaOCuotaDR', str(traslado_data.get('tasa_cuota')))  # valor del impuesto que se envia
            traslado.setAttribute('ImporteDR', str(traslado_data.get('importe')))
        return traslado

    def get_impuestos_pago(self, complemento_data):
        try:
            impuestos_p = self.dom.createElement('pago20:ImpuestosP')
            if len(complemento_data.get('impuestos_retenidos', [])) > 0:
                retenciones = self.dom.createElement('pago20:RetencionesP')
                for retencion_data in complemento_data.get('impuestos_retenidos'):
                    retenciones.appendChild(self.get_retenciones_pago(retencion_data))
                impuestos_p.appendChild(retenciones)
            if len(complemento_data.get('impuestos_trasladados', [])) > 0:
                traslados = self.dom.createElement('pago20:TrasladosP')
                for traslado_data in complemento_data.get('impuestos_trasladados'):
                    traslados.appendChild(self.get_traslados_pago(traslado_data))
                impuestos_p.appendChild(traslados)
            return impuestos_p
        except Exception as e:
            raise Exception("Ocurrio un error al agregar los impuestos en complemento de pago. Error::: " + str(e))

    def get_traslados_pago(self, traslado_data):
        traslado = self.dom.createElement('pago20:TrasladoP')
        traslado.setAttribute('BaseP', str(traslado_data.get('base')))
        traslado.setAttribute('ImpuestoP', traslado_data.get('impuesto'))
        traslado.setAttribute('TipoFactorP', traslado_data.get('tipo_factor'))
        if traslado_data.get('tasa_cuota'):
            traslado.setAttribute('TasaOCuotaP', str(traslado_data.get('tasa_cuota')))
        if traslado_data.get('importe'):
            traslado.setAttribute('ImporteP', str(traslado_data.get('importe')))
        return traslado

    def get_retenciones_pago(self, retencion_data):
        retencion = self.dom.createElement('pago20:RetencionP')
        retencion.setAttribute('ImpuestoP', retencion_data.get('impuesto'))
        retencion.setAttribute('ImporteP', str(retencion_data.get('importe')))
        return retencion
    # ***** Impuestos Pago *****

    def get_addenda(self):
        try:
            addenda = self.dom.createElement('cfdi:Addenda')
            return addenda
        except Exception as e:
            raise Exception("Ocurrio un error. Error::: " + str(e))

    def get_conceptos(self, conceptos_list):
        conceptos = self.dom.createElement('cfdi:Conceptos')
        for concepto in conceptos_list:
            try:
                cfdi_concepto = self.dom.createElement('cfdi:Concepto')
                cfdi_concepto.setAttribute('ClaveProdServ', concepto.get('clave_prod_serv'))

                if concepto.get('no_identificacion'):
                    cfdi_concepto.setAttribute('NoIdentificacion', concepto.get('no_identificacion'))

                cfdi_concepto.setAttribute('Cantidad', str(concepto.get('cantidad')))
                cfdi_concepto.setAttribute('ClaveUnidad', concepto.get('clave_unidad'))

                if concepto.get('unidad'):
                    cfdi_concepto.setAttribute('Unidad', concepto.get('unidad'))

                if concepto.get('descripcion', '') == '':
                    raise Exception('Se debe especificar una descripción para el concepto')

                cfdi_concepto.setAttribute('Descripcion', replace(concepto.get('descripcion', '').strip()))
                cfdi_concepto.setAttribute('ValorUnitario', str(concepto.get('valor_unitario')))
                cfdi_concepto.setAttribute('Importe', str(concepto.get('importe')))
                if concepto.get('descuento') and concepto.get('descuento') not in ['0', '0.00', '0.000000'] :
                    cfdi_concepto.setAttribute('Descuento', str(concepto.get('descuento')))
                cfdi_concepto.setAttribute('ObjetoImp', concepto.get('objeto_impuesto'))

                if self.tipo_comprobante != TRASLADO and concepto.get('objeto_impuesto') == '02':
                    #revisar en el manual si lleva impuestos este tipo de comprobante
                    cfdi_concepto.appendChild(self.get_impuestos_concepto(concepto))

                if concepto.get('informacion_aduanera'):
                    cfdi_concepto.appendChild(self.get_informacion_aduanera(concepto.get('informacion_aduanera')))

                if concepto.get('cuenta_predial'):
                    cfdi_concepto.appendChild(self.get_cuenta_predial(concepto.get('cuenta_predial')))

                conceptos.appendChild(cfdi_concepto)
            except Exception as e:
                raise Exception("Ocurrio un error al agregar los conceptos. Error::: " + str(e))
        return conceptos

    def get_impuestos_concepto(self,concepto):
        impuestos = self.dom.createElement('cfdi:Impuestos')
        if len(concepto.get('traslados', [])) > 0:
            traslados = self.dom.createElement('cfdi:Traslados')
            for traslado in concepto.get('traslados', []):
                traslados.appendChild(self.get_traslados_concepto(traslado))
            impuestos.appendChild(traslados)
        if len(concepto.get('retenciones', [])) > 0:
            retenciones = self.dom.createElement('cfdi:Retenciones')
            for retencion in concepto.get('retenciones', []):
                retenciones.appendChild(self.get_retenciones_concepto(retencion))
            impuestos.appendChild(retenciones)
        return impuestos

    def get_traslados_concepto(self, traslado_data):
        traslado = self.dom.createElement('cfdi:Traslado')
        traslado.setAttribute('Base', str(traslado_data.get('base')))  # Importe del concepto
        traslado.setAttribute('Impuesto', traslado_data.get('impuesto', ''))
        traslado.setAttribute('TipoFactor', traslado_data.get('tipo_factor', 'Tasa'))
        if traslado_data.get('tipo_factor') != 'Exento':
            traslado.setAttribute('TasaOCuota', str(traslado_data.get('tasa_cuota')))
            traslado.setAttribute('Importe', str(traslado_data.get('importe')))
        return traslado

    def get_retenciones_concepto(self, retencion_data):
        retencion = self.dom.createElement('cfdi:Retencion')
        retencion.setAttribute('Base', str(retencion_data.get('base')))  # Importe del concepto
        retencion.setAttribute('Impuesto', retencion_data.get('impuesto'))
        retencion.setAttribute('TipoFactor', retencion_data.get('tipo_factor', 'Tasa'))  # Tipo factor Tasa ó Cuota
        if retencion_data.get('tipo_factor') != 'Exento':
            retencion.setAttribute('TasaOCuota', str(retencion_data.get('tasa_cuota')))  # valor del impuesto que se envia
            retencion.setAttribute('Importe', str(retencion_data.get('importe')))
        return retencion

    def get_informacion_aduanera(self, informacion_aduanera):
        try:
            informacionaduanera = self.dom.createElement('cfdi:InformacionAduanera ')
            informacionaduanera.setAttribute('NumeroPedimento', informacion_aduanera.numeroPedimento)
            return informacionaduanera
        except Exception as e:
            raise Exception("Ocurrio un error. Error::: " + str(e))

    def get_cuenta_predial(self, cuenta_predial):
        try:
            cuentapredial = self.dom.createElement('cfdi:CuentaPredial ')
            cuentapredial.setAttribute('Numero', cuenta_predial)
            return cuentapredial
        except Exception as e:
            raise Exception("Ocurrio un error. Error::: " + str(e))

    def get_parte(self, ingreso_parte):
        try:
            parte = self.dom.createElement('cfdi:CfdiParte')
            parte.setAttribute('ClaveProdServ',ingreso_parte.claveProdServ)
            if ingreso_parte.noIdentificacion:
                parte.setAttribute('NoIdentificacion',ingreso_parte.noIdentificacion)
            parte.setAttribute('Cantidad',str(ingreso_parte.cantidad))
            if len(ingreso_parte.descripcion) > 0:
                parte.setAttribute('Descripcion',replace(ingreso_parte.descripcion.strip()))
            else:
                parte.setAttribute('Descripcion','N/A')
            parte.setAttribute('ValorUnitario',str(ingreso_parte.importe))
            parte.setAttribute('Importe',str(ingreso_parte.importe))
            if ingreso_parte.informacionAduanera:
                parte.appendChild(self.get_informacion_aduanera(ingreso_parte.informacionAduanera))  # No se usara
            return parte
        except Exception as e:
            raise Exception("Ocurrio un error. Error::: " + str(e))

    def get_complemento_cartaporte20(self):
        try:
            cartaporte = self.dom.createElement('cartaporte20:CartaPorte')
            cartaporte.setAttribute('Version', '2.0')
            cartaporte.setAttribute('TranspInternac', self.data.get('TranspInternac'))
            if self.data.get('TranspInternac') == 'Si':
                if self.data.get('EntradaSalidaMerc', '') not in ['Entrada', 'Salida']:
                    raise Exception('El valor del campo EntradaSalidaMerc debe ser: Entrada ó Salida')
                cartaporte.setAttribute('EntradaSalidaMerc', self.data.get('EntradaSalidaMerc'))
                cartaporte.setAttribute('ViaEntradaSalida', self.data.get('ViaEntradaSalida'))

            cartaporte_ubicaciones = self.dom.createElement('cartaporte20:Ubicaciones')
            ubicaciones = self.data.get('ubicaciones', [])
            total_distancia_recorrida = 0
            for ubicacion_data in ubicaciones:
                cartaporte_ubicacion = self.dom.createElement('cartaporte20:Ubicacion')
                destination_counter = 1
                if ubicacion_data.get('type') == 'origen':
                    cartaporte_ubicacion.setAttribute('IDUbicacion', 'OR{}'.format('000001'))
                    cartaporte_ubicacion.setAttribute('TipoUbicacion', 'Origen')
                    cartaporte_ubicacion.setAttribute('RFCRemitenteDestinatario', ubicacion_data.get('RFCRemitente'))
                    cartaporte_ubicacion.setAttribute('FechaHoraSalidaLlegada', ubicacion_data.get('FechaHoraSalida'))
                elif ubicacion_data.get('type') == 'destino':
                    cartaporte_ubicacion.setAttribute('IDUbicacion', 'DE00000{}'.format(destination_counter))
                    cartaporte_ubicacion.setAttribute('DistanciaRecorrida', str(ubicacion_data.get('DistanciaRecorrida')))
                    cartaporte_ubicacion.setAttribute('TipoUbicacion', 'Destino')
                    cartaporte_ubicacion.setAttribute('RFCRemitenteDestinatario', ubicacion_data.get('RFCDestinatario'))
                    cartaporte_ubicacion.setAttribute('FechaHoraSalidaLlegada', ubicacion_data.get('FechaHoraProgLlegada'))
                    total_distancia_recorrida += float(ubicacion_data.get('DistanciaRecorrida'))
                    destination_counter += 1

                cartaporte_ubicacion_domicilio = self.dom.createElement('cartaporte20:Domicilio')
                cartaporte_ubicacion_domicilio.setAttribute('Calle', ubicacion_data.get('Calle'))
                if ubicacion_data.get('NumeroExterior') != '':
                    cartaporte_ubicacion_domicilio.setAttribute('NumeroExterior', ubicacion_data.get('NumeroExterior'))
                if ubicacion_data.get('Colonia') != '':
                    cartaporte_ubicacion_domicilio.setAttribute('Colonia', ubicacion_data.get('Colonia'))
                if ubicacion_data.get('Localidad') != '':
                    cartaporte_ubicacion_domicilio.setAttribute('Localidad', ubicacion_data.get('Localidad'))
                if ubicacion_data.get('Referencia') != '':
                    cartaporte_ubicacion_domicilio.setAttribute('Referencia', ubicacion_data.get('Referencia'))
                cartaporte_ubicacion_domicilio.setAttribute('Municipio', ubicacion_data.get('Municipio'))
                cartaporte_ubicacion_domicilio.setAttribute('Estado', ubicacion_data.get('Estado'))
                cartaporte_ubicacion_domicilio.setAttribute('Pais', ubicacion_data.get('Pais'))
                cartaporte_ubicacion_domicilio.setAttribute('CodigoPostal', ubicacion_data.get('CodigoPostal'))
                cartaporte_ubicacion.appendChild(cartaporte_ubicacion_domicilio)
                cartaporte_ubicaciones.appendChild(cartaporte_ubicacion)
            cartaporte.appendChild(cartaporte_ubicaciones)
            if self.tipo_transporte in ['AutotransporteFederal', 'TransporteFerroviario']:
                cartaporte.setAttribute('TotalDistRec', str(round(total_distancia_recorrida, 3)))

            cartaporte_mercancias = self.dom.createElement('cartaporte20:Mercancias')
            mercancias = self.data.get('mercancias', [])
            num_total_mercancias = 0
            peso_bruto = 0
            for mercancia_data in mercancias:
                cartaporte_mercancia = self.dom.createElement('cartaporte20:Mercancia')
                if mercancia_data.get('BienesTransp') is not None:
                    cartaporte_mercancia.setAttribute('BienesTransp', mercancia_data.get('BienesTransp'))
                    cartaporte_mercancia.setAttribute('Descripcion', mercancia_data.get('Descripcion'))
                    cartaporte_mercancia.setAttribute('Cantidad', mercancia_data.get('Cantidad'))
                    cartaporte_mercancia.setAttribute('ClaveUnidad', mercancia_data.get('ClaveUnidad'))
                cartaporte_mercancia.setAttribute('PesoEnKg', mercancia_data.get('PesoEnKg'))
                cartaporte_mercancia.setAttribute('ValorMercancia', mercancia_data.get('ValorMercancia'))
                cartaporte_mercancia.setAttribute('Moneda', mercancia_data.get('Moneda'))

                if mercancia_data.get('MaterialPeligroso') == 'No':
                    cartaporte_mercancia.setAttribute('MaterialPeligroso', mercancia_data.get('MaterialPeligroso', ''))

                if mercancia_data.get('MaterialPeligroso') == 'Sí':
                    cartaporte_mercancia.setAttribute('MaterialPeligroso', mercancia_data.get('MaterialPeligroso'))
                    cartaporte_mercancia.setAttribute('CveMaterialPeligroso', mercancia_data.get('CveMaterialPeligroso'))
                    cartaporte_mercancia.setAttribute('Embalaje', mercancia_data.get('Embalaje'))
                    cartaporte_mercancia.setAttribute('DescripEmbalaje', mercancia_data.get('DescripEmbalaje'))

                cartaporte_mercancias.appendChild(cartaporte_mercancia)
                num_total_mercancias += 1
                peso_bruto += float(mercancia_data.get('PesoEnKg'))

                cartaporte_mercancia_cantidad_transporta = self.dom.createElement('cartaporte20:CantidadTransporta')
                cartaporte_mercancia_cantidad_transporta.setAttribute('Cantidad', mercancia_data.get('Cantidad'))
                cartaporte_mercancia_cantidad_transporta.setAttribute('IDOrigen', 'OR000001')
                cartaporte_mercancia_cantidad_transporta.setAttribute('IDDestino', 'DE000001')
                cartaporte_mercancia.appendChild(cartaporte_mercancia_cantidad_transporta)

            cartaporte_mercancias.setAttribute('NumTotalMercancias', str(num_total_mercancias))
            cartaporte_mercancias.setAttribute('PesoBrutoTotal', str(round(peso_bruto, 3)))
            cartaporte_mercancias.setAttribute('UnidadPeso', 'KGM')
            cartaporte.appendChild(cartaporte_mercancias)

            if self.tipo_transporte not in ['AutotransporteFederal', 'TransporteMaritimo', 'TransporteAereo', 'TransporteFerroviario']:
                raise Exception('Se debe registrar un tipo de transporte')
            transporte_data = self.data.get('transporte')
            if self.tipo_transporte == 'AutotransporteFederal':
                cartaporte_tipo_transporte = self.dom.createElement('cartaporte20:Autotransporte')
                cartaporte_tipo_transporte.setAttribute('PermSCT', transporte_data.get('PermSCT'))
                cartaporte_tipo_transporte.setAttribute('NumPermisoSCT', transporte_data.get('NumPermisoSCT'))

                cartaporte_identificacion_vehicular = self.dom.createElement('cartaporte20:IdentificacionVehicular')
                cartaporte_identificacion_vehicular.setAttribute('ConfigVehicular', transporte_data.get('ConfigVehicular'))
                cartaporte_identificacion_vehicular.setAttribute('PlacaVM', transporte_data.get('PlacaVM'))
                cartaporte_identificacion_vehicular.setAttribute('AnioModeloVM', transporte_data.get('AnioModeloVM'))
                cartaporte_tipo_transporte.appendChild(cartaporte_identificacion_vehicular)


                cartaporte_seguros = self.dom.createElement('cartaporte20:Seguros')
                cartaporte_seguros.setAttribute('AseguraRespCivil', transporte_data.get('NombreAseg'))
                cartaporte_seguros.setAttribute('PolizaRespCivil', transporte_data.get('NumPolizaSeguro'))

                cartaporte_tipo_transporte.appendChild(cartaporte_seguros)

                remolques = transporte_data.get('remolques', [])
                if len(remolques) > 0:
                    cartaporte_remolques = self.dom.createElement('cartaporte20:Remolques')
                    for remolque_data in remolques:
                        cartaporte_remolque = self.dom.createElement('cartaporte20:Remolque')
                        cartaporte_remolque.setAttribute('SubTipoRem', remolque_data.get('SubTipoRem'))
                        cartaporte_remolque.setAttribute('Placa', remolque_data.get('Placa'))
                        cartaporte_remolques.appendChild(cartaporte_remolque)
                    cartaporte_tipo_transporte.appendChild(cartaporte_remolques)
                cartaporte_mercancias.appendChild(cartaporte_tipo_transporte)

            cartaporte_figura_transporte = self.dom.createElement('cartaporte20:FiguraTransporte')

            operadores = transporte_data.get('operadores', [])
            for operador_data in operadores:
                cartaporte_operador = self.dom.createElement('cartaporte20:TiposFigura')
                cartaporte_operador.setAttribute('TipoFigura', '01')
                cartaporte_operador.setAttribute('RFCFigura', operador_data.get('RFCOperador'))
                cartaporte_operador.setAttribute('NumLicencia', operador_data.get('NumLicencia'))
                cartaporte_figura_transporte.appendChild(cartaporte_operador)

            cartaporte.appendChild(cartaporte_figura_transporte)

            return cartaporte
        except Exception as e:
            raise Exception("Ocurrio un error al generar el complemento cartaporte. Error::: " + str(e))

    def get_complemento_cartaporte30(self):
        try:
            cartaporte_data = self.data.get('complemento_cartaporte')
            cartaporte = self.dom.createElement('cartaporte30:CartaPorte')
            cartaporte.setAttribute('Version', '3.0')
            cartaporte.setAttribute('IdCCP', cartaporte_data.get('IdCCP')) # nuevo - identificador complemento carta porte
            cartaporte.setAttribute('TranspInternac', cartaporte_data.get('TranspInternac'))
            if cartaporte_data.get('TranspInternac') == 'Si':
                if cartaporte_data.get('EntradaSalidaMerc', '') not in ['Entrada', 'Salida']:
                    raise Exception('El valor del campo EntradaSalidaMerc debe ser: Entrada ó Salida')
                cartaporte.setAttribute('RegimenAduanero', cartaporte_data.get('RegimenAduanero'))  # nuevo
                cartaporte.setAttribute('EntradaSalidaMerc', cartaporte_data.get('EntradaSalidaMerc'))
                cartaporte.setAttribute('PaisOrigenDestino', cartaporte_data.get('PaisOrigenDestino'))
                cartaporte.setAttribute('ViaEntradaSalida', cartaporte_data.get('ViaEntradaSalida'))

            cartaporte_ubicaciones = self.dom.createElement('cartaporte30:Ubicaciones')
            ubicaciones = cartaporte_data.get('ubicaciones', [])
            total_distancia_recorrida = 0
            for ubicacion_data in ubicaciones:
                cartaporte_ubicacion = self.dom.createElement('cartaporte30:Ubicacion')
                destination_counter = 1
                if ubicacion_data.get('type') == 'origen':
                    cartaporte_ubicacion.setAttribute('IDUbicacion', 'OR{}'.format('000001'))
                    cartaporte_ubicacion.setAttribute('TipoUbicacion', 'Origen')

                elif ubicacion_data.get('type') == 'destino':
                    cartaporte_ubicacion.setAttribute('IDUbicacion', 'DE00000{}'.format(destination_counter))
                    cartaporte_ubicacion.setAttribute('TipoUbicacion', 'Destino')

                cartaporte_ubicacion.setAttribute('RFCRemitenteDestinatario', ubicacion_data.get('RFCRemitenteDestinatario'))
                cartaporte_ubicacion.setAttribute('NombreRemitenteDestinatario', ubicacion_data.get('NombreRemitenteDestinatario'))  # nuevo
                if ubicacion_data.get('RFCRemitenteDestinatario') == 'XEXX010101000':
                    cartaporte_ubicacion.setAttribute('NumRegIdTrib', ubicacion_data.get('NumRegIdTrib'))  # nuevo
                    cartaporte_ubicacion.setAttribute('ResidenciaFiscal', ubicacion_data.get('ResidenciaFiscal'))  # nuevo
                cartaporte_ubicacion.setAttribute('FechaHoraSalidaLlegada', ubicacion_data.get('FechaHoraSalidaLlegada'))

                if ubicacion_data.get('type') == 'destino':
                    cartaporte_ubicacion.setAttribute('DistanciaRecorrida', str(ubicacion_data.get('DistanciaRecorrida')))
                    total_distancia_recorrida += float(ubicacion_data.get('DistanciaRecorrida'))
                    destination_counter += 1

                cartaporte_ubicacion_domicilio = self.dom.createElement('cartaporte30:Domicilio')
                cartaporte_ubicacion_domicilio.setAttribute('Calle', ubicacion_data.get('Calle'))
                if ubicacion_data.get('NumeroExterior') != '':
                    cartaporte_ubicacion_domicilio.setAttribute('NumeroExterior', ubicacion_data.get('NumeroExterior'))
                if ubicacion_data.get('NumeroInterior') != '':
                    cartaporte_ubicacion_domicilio.setAttribute('NumeroInterior', ubicacion_data.get('NumeroInterior'))
                if ubicacion_data.get('Colonia') != '':
                    cartaporte_ubicacion_domicilio.setAttribute('Colonia', ubicacion_data.get('Colonia'))
                if ubicacion_data.get('Localidad') != '':
                    cartaporte_ubicacion_domicilio.setAttribute('Localidad', ubicacion_data.get('Localidad'))
                if ubicacion_data.get('Referencia') != '':
                    cartaporte_ubicacion_domicilio.setAttribute('Referencia', ubicacion_data.get('Referencia'))
                if ubicacion_data.get('Municipio') != '':
                    cartaporte_ubicacion_domicilio.setAttribute('Municipio', ubicacion_data.get('Municipio'))
                cartaporte_ubicacion_domicilio.setAttribute('Estado', ubicacion_data.get('Estado'))
                cartaporte_ubicacion_domicilio.setAttribute('Pais', ubicacion_data.get('Pais'))
                cartaporte_ubicacion_domicilio.setAttribute('CodigoPostal', ubicacion_data.get('CodigoPostal'))
                cartaporte_ubicacion.appendChild(cartaporte_ubicacion_domicilio)
                cartaporte_ubicaciones.appendChild(cartaporte_ubicacion)
            cartaporte.appendChild(cartaporte_ubicaciones)

            if cartaporte_data.get('tipo_transporte') in ['AutotransporteFederal', 'TransporteFerroviario']:
                cartaporte.setAttribute('TotalDistRec', str(round(total_distancia_recorrida, 3)))

            cartaporte_mercancias = self.dom.createElement('cartaporte30:Mercancias')
            mercancias = cartaporte_data.get('mercancias', [])
            num_total_mercancias = 0
            peso_bruto = 0
            for mercancia_data in mercancias:
                cartaporte_mercancia = self.dom.createElement('cartaporte30:Mercancia')
                if mercancia_data.get('BienesTransp'):
                    cartaporte_mercancia.setAttribute('BienesTransp', mercancia_data.get('BienesTransp'))
                    cartaporte_mercancia.setAttribute('Descripcion', mercancia_data.get('Descripcion'))
                    cartaporte_mercancia.setAttribute('Cantidad', mercancia_data.get('Cantidad'))
                    cartaporte_mercancia.setAttribute('ClaveUnidad', mercancia_data.get('ClaveUnidad'))
                cartaporte_mercancia.setAttribute('PesoEnKg', mercancia_data.get('PesoEnKg'))
                cartaporte_mercancia.setAttribute('ValorMercancia', mercancia_data.get('ValorMercancia'))
                cartaporte_mercancia.setAttribute('Moneda', mercancia_data.get('Moneda'))

                if mercancia_data.get('MaterialPeligroso') == 'No':
                    cartaporte_mercancia.setAttribute('MaterialPeligroso', mercancia_data.get('MaterialPeligroso', ''))

                if mercancia_data.get('MaterialPeligroso') == 'Sí':
                    cartaporte_mercancia.setAttribute('MaterialPeligroso', mercancia_data.get('MaterialPeligroso', ''))
                    cartaporte_mercancia.setAttribute('CveMaterialPeligroso', mercancia_data.get('CveMaterialPeligroso'))
                    cartaporte_mercancia.setAttribute('Embalaje', mercancia_data.get('Embalaje'))
                    cartaporte_mercancia.setAttribute('DescripEmbalaje', mercancia_data.get('DescripEmbalaje'))

                cartaporte_mercancias.appendChild(cartaporte_mercancia)
                num_total_mercancias += 1
                peso_bruto += float(mercancia_data.get('PesoEnKg'))

                cartaporte_mercancia_cantidad_transporta = self.dom.createElement('cartaporte30:CantidadTransporta')
                cartaporte_mercancia_cantidad_transporta.setAttribute('Cantidad', mercancia_data.get('Cantidad'))
                cartaporte_mercancia_cantidad_transporta.setAttribute('IDOrigen', 'OR000001')
                cartaporte_mercancia_cantidad_transporta.setAttribute('IDDestino', 'DE000001')
                cartaporte_mercancia.appendChild(cartaporte_mercancia_cantidad_transporta)

            cartaporte_mercancias.setAttribute('NumTotalMercancias', str(num_total_mercancias))
            cartaporte_mercancias.setAttribute('PesoBrutoTotal', str(round(peso_bruto, 3)))
            cartaporte_mercancias.setAttribute('UnidadPeso', 'KGM')
            cartaporte.appendChild(cartaporte_mercancias)

            if cartaporte_data.get('tipo_transporte') not in ['AutotransporteFederal', 'TransporteMaritimo', 'TransporteAereo', 'TransporteFerroviario']:
                raise Exception('Se debe registrar un tipo de transporte')
            transporte_data = cartaporte_data.get('transporte')
            if cartaporte_data.get('tipo_transporte') == 'AutotransporteFederal':
                cartaporte_tipo_transporte = self.dom.createElement('cartaporte30:Autotransporte')
                cartaporte_tipo_transporte.setAttribute('PermSCT', transporte_data.get('PermSCT'))
                cartaporte_tipo_transporte.setAttribute('NumPermisoSCT', transporte_data.get('NumPermisoSCT'))

                cartaporte_identificacion_vehicular = self.dom.createElement('cartaporte30:IdentificacionVehicular')
                cartaporte_identificacion_vehicular.setAttribute('ConfigVehicular', transporte_data.get('ConfigVehicular'))
                cartaporte_identificacion_vehicular.setAttribute('PesoBrutoVehicular', transporte_data.get('PesoBrutoVehicular'))
                cartaporte_identificacion_vehicular.setAttribute('PlacaVM', transporte_data.get('PlacaVM'))
                cartaporte_identificacion_vehicular.setAttribute('AnioModeloVM', transporte_data.get('AnioModeloVM'))
                cartaporte_tipo_transporte.appendChild(cartaporte_identificacion_vehicular)


                cartaporte_seguros = self.dom.createElement('cartaporte30:Seguros')
                cartaporte_seguros.setAttribute('AseguraRespCivil', transporte_data.get('NombreAseg'))
                cartaporte_seguros.setAttribute('PolizaRespCivil', transporte_data.get('NumPolizaSeguro'))

                cartaporte_tipo_transporte.appendChild(cartaporte_seguros)

                remolques = transporte_data.get('remolques', [])
                if len(remolques) > 0:
                    cartaporte_remolques = self.dom.createElement('cartaporte30:Remolques')
                    for remolque_data in remolques:
                        cartaporte_remolque = self.dom.createElement('cartaporte30:Remolque')
                        cartaporte_remolque.setAttribute('SubTipoRem', remolque_data.get('SubTipoRem'))
                        cartaporte_remolque.setAttribute('Placa', remolque_data.get('Placa'))
                        cartaporte_remolques.appendChild(cartaporte_remolque)
                    cartaporte_tipo_transporte.appendChild(cartaporte_remolques)
                cartaporte_mercancias.appendChild(cartaporte_tipo_transporte)

            cartaporte_figura_transporte = self.dom.createElement('cartaporte30:FiguraTransporte')

            operadores = transporte_data.get('operadores', [])
            for operador_data in operadores:
                cartaporte_operador = self.dom.createElement('cartaporte30:TiposFigura')
                cartaporte_operador.setAttribute('TipoFigura', '01')
                cartaporte_operador.setAttribute('RFCFigura', operador_data.get('RFCFigura'))
                cartaporte_operador.setAttribute('NombreFigura', operador_data.get('NombreFigura'))
                cartaporte_operador.setAttribute('NumLicencia', operador_data.get('NumLicencia'))
                cartaporte_figura_transporte.appendChild(cartaporte_operador)

            cartaporte.appendChild(cartaporte_figura_transporte)

            return cartaporte
        except Exception as e:
            raise Exception("Ocurrio un error al generar el complemento cartaporte. Error::: " + str(e))

    def get_complemento_cartaporte31(self):
        try:
            cartaporte_data = self.data.get('complemento_cartaporte')
            cartaporte = self.dom.createElement('cartaporte31:CartaPorte')
            cartaporte.setAttribute('Version', '3.1')
            cartaporte.setAttribute('IdCCP', cartaporte_data.get('IdCCP')) # nuevo - identificador complemento carta porte
            cartaporte.setAttribute('TranspInternac', cartaporte_data.get('TranspInternac'))

            if cartaporte_data.get('RegistroISTMO'):
                cartaporte.setAttribute('RegistroISTMO', cartaporte_data.get('RegistroISTMO'))
            if cartaporte_data.get('UbicacionPoloOrigen'):
                cartaporte.setAttribute('UbicacionPoloOrigen', cartaporte_data.get('UbicacionPoloOrigen'))
            if cartaporte_data.get('UbicacionPoloDestino'):
                cartaporte.setAttribute('UbicacionPoloDestino', cartaporte_data.get('UbicacionPoloDestino'))

            if cartaporte_data.get('TranspInternac') == 'Si':
                if cartaporte_data.get('EntradaSalidaMerc', '') not in ['Entrada', 'Salida']:
                    raise Exception('El valor del campo EntradaSalidaMerc debe ser: Entrada ó Salida')
                #cartaporte.setAttribute('RegimenAduanero', cartaporte_data.get('RegimenAduanero'))  # nuevo
                cartaporte.setAttribute('EntradaSalidaMerc', cartaporte_data.get('EntradaSalidaMerc'))
                cartaporte.setAttribute('PaisOrigenDestino', cartaporte_data.get('PaisOrigenDestino'))
                cartaporte.setAttribute('ViaEntradaSalida', cartaporte_data.get('ViaEntradaSalida'))

                cartaporte_regimenes_aduaneros = self.dom.createElement('cartaporte31:RegimenesAduaneros')
                cartaporte_regimen_aduanero = self.dom.createElement('cartaporte31:RegimenAduaneroCCP')
                cartaporte_regimen_aduanero.setAttribute('RegimenAduanero', cartaporte_data.get('RegimenAduanero'))
                cartaporte_regimenes_aduaneros.appendChild(cartaporte_regimen_aduanero)


            cartaporte_ubicaciones = self.dom.createElement('cartaporte31:Ubicaciones')
            ubicaciones = cartaporte_data.get('ubicaciones', [])
            total_distancia_recorrida = 0
            for ubicacion_data in ubicaciones:
                cartaporte_ubicacion = self.dom.createElement('cartaporte31:Ubicacion')
                destination_counter = 1
                if ubicacion_data.get('type') == 'origen':
                    cartaporte_ubicacion.setAttribute('IDUbicacion', 'OR{}'.format('000001'))
                    cartaporte_ubicacion.setAttribute('TipoUbicacion', 'Origen')

                elif ubicacion_data.get('type') == 'destino':
                    cartaporte_ubicacion.setAttribute('IDUbicacion', 'DE00000{}'.format(destination_counter))
                    cartaporte_ubicacion.setAttribute('TipoUbicacion', 'Destino')

                cartaporte_ubicacion.setAttribute('RFCRemitenteDestinatario', ubicacion_data.get('RFCRemitenteDestinatario'))
                cartaporte_ubicacion.setAttribute('NombreRemitenteDestinatario', ubicacion_data.get('NombreRemitenteDestinatario'))  # nuevo
                if ubicacion_data.get('RFCRemitenteDestinatario') == 'XEXX010101000':
                    cartaporte_ubicacion.setAttribute('NumRegIdTrib', ubicacion_data.get('NumRegIdTrib'))  # nuevo
                    cartaporte_ubicacion.setAttribute('ResidenciaFiscal', ubicacion_data.get('ResidenciaFiscal'))  # nuevo
                cartaporte_ubicacion.setAttribute('FechaHoraSalidaLlegada', ubicacion_data.get('FechaHoraSalidaLlegada'))

                if ubicacion_data.get('type') == 'destino':
                    cartaporte_ubicacion.setAttribute('DistanciaRecorrida', str(ubicacion_data.get('DistanciaRecorrida')))
                    total_distancia_recorrida += float(ubicacion_data.get('DistanciaRecorrida'))
                    destination_counter += 1

                cartaporte_ubicacion_domicilio = self.dom.createElement('cartaporte31:Domicilio')
                cartaporte_ubicacion_domicilio.setAttribute('Calle', ubicacion_data.get('Calle'))
                if ubicacion_data.get('NumeroExterior') != '':
                    cartaporte_ubicacion_domicilio.setAttribute('NumeroExterior', ubicacion_data.get('NumeroExterior'))
                if ubicacion_data.get('NumeroInterior') != '':
                    cartaporte_ubicacion_domicilio.setAttribute('NumeroInterior', ubicacion_data.get('NumeroInterior'))
                if ubicacion_data.get('Colonia') != '':
                    cartaporte_ubicacion_domicilio.setAttribute('Colonia', ubicacion_data.get('Colonia'))
                if ubicacion_data.get('Localidad') != '':
                    cartaporte_ubicacion_domicilio.setAttribute('Localidad', ubicacion_data.get('Localidad'))
                if ubicacion_data.get('Referencia') != '':
                    cartaporte_ubicacion_domicilio.setAttribute('Referencia', ubicacion_data.get('Referencia'))
                if ubicacion_data.get('Municipio') != '':
                    cartaporte_ubicacion_domicilio.setAttribute('Municipio', ubicacion_data.get('Municipio'))
                cartaporte_ubicacion_domicilio.setAttribute('Estado', ubicacion_data.get('Estado'))
                cartaporte_ubicacion_domicilio.setAttribute('Pais', ubicacion_data.get('Pais'))
                cartaporte_ubicacion_domicilio.setAttribute('CodigoPostal', ubicacion_data.get('CodigoPostal'))
                cartaporte_ubicacion.appendChild(cartaporte_ubicacion_domicilio)
                cartaporte_ubicaciones.appendChild(cartaporte_ubicacion)
            cartaporte.appendChild(cartaporte_ubicaciones)

            if cartaporte_data.get('tipo_transporte') in ['AutotransporteFederal', 'TransporteFerroviario']:
                cartaporte.setAttribute('TotalDistRec', str(round(total_distancia_recorrida, 3)))

            cartaporte_mercancias = self.dom.createElement('cartaporte31:Mercancias')
            mercancias = cartaporte_data.get('mercancias', [])
            num_total_mercancias = 0
            peso_bruto = 0
            for mercancia_data in mercancias:
                cartaporte_mercancia = self.dom.createElement('cartaporte31:Mercancia')
                if mercancia_data.get('BienesTransp'):
                    cartaporte_mercancia.setAttribute('BienesTransp', mercancia_data.get('BienesTransp'))
                    cartaporte_mercancia.setAttribute('Descripcion', mercancia_data.get('Descripcion'))
                    cartaporte_mercancia.setAttribute('Cantidad', mercancia_data.get('Cantidad'))
                    cartaporte_mercancia.setAttribute('ClaveUnidad', mercancia_data.get('ClaveUnidad'))
                cartaporte_mercancia.setAttribute('PesoEnKg', mercancia_data.get('PesoEnKg'))
                cartaporte_mercancia.setAttribute('ValorMercancia', mercancia_data.get('ValorMercancia'))
                cartaporte_mercancia.setAttribute('Moneda', mercancia_data.get('Moneda'))

                if mercancia_data.get('MaterialPeligroso') == 'No':
                    cartaporte_mercancia.setAttribute('MaterialPeligroso', mercancia_data.get('MaterialPeligroso', ''))

                if mercancia_data.get('MaterialPeligroso') == 'Sí':
                    cartaporte_mercancia.setAttribute('MaterialPeligroso', mercancia_data.get('MaterialPeligroso', ''))
                    cartaporte_mercancia.setAttribute('CveMaterialPeligroso', mercancia_data.get('CveMaterialPeligroso'))
                    cartaporte_mercancia.setAttribute('Embalaje', mercancia_data.get('Embalaje'))
                    cartaporte_mercancia.setAttribute('DescripEmbalaje', mercancia_data.get('DescripEmbalaje'))

                cartaporte_mercancias.appendChild(cartaporte_mercancia)
                num_total_mercancias += 1
                peso_bruto += float(mercancia_data.get('PesoEnKg'))

                cartaporte_mercancia_cantidad_transporta = self.dom.createElement('cartaporte31:CantidadTransporta')
                cartaporte_mercancia_cantidad_transporta.setAttribute('Cantidad', mercancia_data.get('Cantidad'))
                cartaporte_mercancia_cantidad_transporta.setAttribute('IDOrigen', 'OR000001')
                cartaporte_mercancia_cantidad_transporta.setAttribute('IDDestino', 'DE000001')
                cartaporte_mercancia.appendChild(cartaporte_mercancia_cantidad_transporta)

            cartaporte_mercancias.setAttribute('NumTotalMercancias', str(num_total_mercancias))
            cartaporte_mercancias.setAttribute('PesoBrutoTotal', str(round(peso_bruto, 3)))
            cartaporte_mercancias.setAttribute('UnidadPeso', 'KGM')
            cartaporte.appendChild(cartaporte_mercancias)

            if cartaporte_data.get('tipo_transporte') not in ['AutotransporteFederal', 'TransporteMaritimo', 'TransporteAereo', 'TransporteFerroviario']:
                raise Exception('Se debe registrar un tipo de transporte')
            transporte_data = cartaporte_data.get('transporte')
            if cartaporte_data.get('tipo_transporte') == 'AutotransporteFederal':
                cartaporte_tipo_transporte = self.dom.createElement('cartaporte31:Autotransporte')
                cartaporte_tipo_transporte.setAttribute('PermSCT', transporte_data.get('PermSCT'))
                cartaporte_tipo_transporte.setAttribute('NumPermisoSCT', transporte_data.get('NumPermisoSCT'))

                cartaporte_identificacion_vehicular = self.dom.createElement('cartaporte31:IdentificacionVehicular')
                cartaporte_identificacion_vehicular.setAttribute('ConfigVehicular', transporte_data.get('ConfigVehicular'))
                cartaporte_identificacion_vehicular.setAttribute('PesoBrutoVehicular', transporte_data.get('PesoBrutoVehicular'))
                cartaporte_identificacion_vehicular.setAttribute('PlacaVM', transporte_data.get('PlacaVM'))
                cartaporte_identificacion_vehicular.setAttribute('AnioModeloVM', transporte_data.get('AnioModeloVM'))
                cartaporte_tipo_transporte.appendChild(cartaporte_identificacion_vehicular)


                cartaporte_seguros = self.dom.createElement('cartaporte31:Seguros')
                cartaporte_seguros.setAttribute('AseguraRespCivil', transporte_data.get('NombreAseg'))
                cartaporte_seguros.setAttribute('PolizaRespCivil', transporte_data.get('NumPolizaSeguro'))

                cartaporte_tipo_transporte.appendChild(cartaporte_seguros)

                remolques = transporte_data.get('remolques', [])
                if len(remolques) > 0:
                    cartaporte_remolques = self.dom.createElement('cartaporte31:Remolques')
                    for remolque_data in remolques:
                        cartaporte_remolque = self.dom.createElement('cartaporte31:Remolque')
                        cartaporte_remolque.setAttribute('SubTipoRem', remolque_data.get('SubTipoRem'))
                        cartaporte_remolque.setAttribute('Placa', remolque_data.get('Placa'))
                        cartaporte_remolques.appendChild(cartaporte_remolque)
                    cartaporte_tipo_transporte.appendChild(cartaporte_remolques)
                cartaporte_mercancias.appendChild(cartaporte_tipo_transporte)

            cartaporte_figura_transporte = self.dom.createElement('cartaporte31:FiguraTransporte')

            operadores = transporte_data.get('operadores', [])
            for operador_data in operadores:
                cartaporte_operador = self.dom.createElement('cartaporte31:TiposFigura')
                cartaporte_operador.setAttribute('TipoFigura', '01')
                cartaporte_operador.setAttribute('RFCFigura', operador_data.get('RFCFigura'))
                cartaporte_operador.setAttribute('NombreFigura', operador_data.get('NombreFigura'))
                cartaporte_operador.setAttribute('NumLicencia', operador_data.get('NumLicencia'))
                cartaporte_figura_transporte.appendChild(cartaporte_operador)

            cartaporte.appendChild(cartaporte_figura_transporte)

            return cartaporte
        except Exception as e:
            raise Exception("Ocurrio un error al generar el complemento cartaporte. Error::: " + str(e))