import nltk,codecs,json,optparse,sys,re
from jsonrpclib.SimpleJSONRPCServer import SimpleJSONRPCServer, SimpleJSONRPCRequestHandler
from klaseak import *

class HierarkiakKargatu:     
    def __init__(self,inp):
        # self.hierarkiak = {}
        # Hierarkia = ["CLINICAL_DIS","CLINICAL_FIN","BODYSTRUCTURE","ENVIRONMENT","EVENT","FORCE","OBJECT","OBSERVABLE","ORGANISM","PHARMPRODUCT","PROCEDURE","QUALIFIER","RECORD","SITUATION","SOCIAL","SPECIAL","SPECIMEN","STAGING","SUBSTANCE"]
        # for hie in Hierarkia:
        #     for syn in ["_pre_eng.txt",'_syn_eng.txt']:
        #         f = '../../../euSnomed/snomed/hierarkiak/'+hie+syn
        #         print(f,"kargatzen...")
        #         with codecs.open(f,encoding='utf-8') as fitx:
        #             for line in fitx:
        #                 desk = " ".join(nltk.word_tokenize(line.strip().split('\t')[7].lower()))
        #                 if desk in self.hierarkiak:
        #                     lag = self.hierarkiak[desk]
        #                     if hie not in lag:
        #                         self.hierarkiak[desk] = lag + '#' + hie
        #                 else:
        #                     self.hierarkiak[desk] = hie

        m = re.match('.*/SnomedCT_RF([12])Release_([^_]*)_([^/]*)/',inp)
        if m:
            fileType = "sct"+m.group(1)
            namespace = m.group(2)
            version = m.group(3)
        else:
            print('fitxategiaren izena ez da ezagutu')
            exit()
        fitxC = inp+fileType+'_Concepts_Core_'+namespace+'_'+version+'.txt'
        fitxD = inp+fileType+'_Descriptions_eus_'+namespace+'_'+version+'.txt'
        fitxR = inp+fileType+'_Relationships_Core_'+namespace+'_'+version+'.txt'
        self.konZer = ConceptList(fitxC)
        print("Kontzeptuak kargatuta",len(self.konZer.zerrenda))
        self.desZer = DescriptionList(fitxD,self.konZer)
        print("Deskribapenak kargatuta",len(self.desZer.zerrenda))
        self.erlZer = RelationshipList(fitxR,self.konZer,True)
        print("Erlazioak kargatuta",len(self.erlZer.umeZerrenda))
        self.erlZer.hierarkiakEsleitu()
        print("Hierarkiak kargatuta",len(self.erlZer.hierarkiak))


    def deskribapenakJaso(self):
        return json.dumps(self.desZer.zerrendaLortu())

    def deskribapenArabera(self):
        return json.dumps(self.desZer.deskribapenArabera())

    def sct2term(self,sctId):
        return json.dumps(self.konZer.sct2term(sctId))

    def sct2desc(self,sctId):
        return json.dumps(self.konZer.sct2desc(sctId))

    def sct2hierarkiak(self,sctId):
        return json.dumps(self.erlZer.hierarkiaLortu(sctId))

    def desc2sct(self,desc,lemma):
        return json.dumps(self.desZer.kodeaLortu(desc,lemma))


def main():
    """
    The code below starts an JSONRPC server
    """
    parser = optparse.OptionParser(usage="%prog [OPTIONS]")
    parser.add_option('-p', '--port', default='8082',
                      help='Port to serve on (default 8082)')
    parser.add_option('-H', '--host', default='127.0.0.1',
                      help='Host to serve on (default localhost; 0.0.0.0 to make public)')
    parser.add_option('-v', '--verbose', action='store_false', default=False, dest='verbose',
                      help="Quiet mode, don't print status msgs to stdout")
    options, args = parser.parse_args()
    VERBOSE = options.verbose
    # server = jsonrpc.Server(jsonrpc.JsonRpc20(),
    #                         jsonrpc.TransportTcpIp(addr=(options.host, int(options.port))))
    try:
        #rh = AllPathRequestHandler if options.ignorepath else SimpleJSONRPCRequestHandler
        rh = SimpleJSONRPCRequestHandler
        server = SimpleJSONRPCServer((options.host, int(options.port)),
                                     requestHandler=rh)
        #inp = '/sc01a7/users/ixamed/BaliabideSemantikoak/SnomedCT_RF1Release_INT_20150131/Terminology/Content/'
        inp = '/ixadata/users/operezdevina001/Doktoretza/kodea/txt2snomed/SnomedCT_RF1Release_eus_20150731'
        des = HierarkiakKargatu(inp)
        server.register_function(des.deskribapenakJaso)
        server.register_function(des.deskribapenArabera)
        server.register_function(des.sct2term)
        server.register_function(des.sct2desc)
        server.register_function(des.sct2hierarkiak)
        server.register_function(des.desc2sct)

        print('Serving on http://%s:%s' % (options.host, options.port))
        # server.serve()
        server.serve_forever()
    except KeyboardInterrupt:
        print(sys.stderr, "Bye.")
        exit()



if __name__ == '__main__':
    main()
