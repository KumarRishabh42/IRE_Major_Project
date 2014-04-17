import wikipedia
import nltk.corpus
import nltk.tag
import itertools
from nltk.tag.stanford import POSTagger
import re


#advertisement='Have awesome Biryani at Paradise'
#advertisement='Watch cricket match live at Star Cricket'
#advertisement='Nike , just do it'
#advertisement='The all new samsung galaxy S5 , in stores now'
#advertisement='The new Iphone 5S is the best iphone ever'
#advertisement='watch tv with exceeding clarity, new Sony 4k Tv'
#advertisement='Captain America, in your nearest theatre on April 4'
#advertisement='get your weekly dose of Game of Thrones today , subscribe to HBO'
#advertisement='Royal Stag , its your life make it large'
#advertisement='John the great died very quickly'
advertisement='An Apple a day keeps the doctor away'
#advertisement='by an apple'
#advertisement='you cannot buy happiness , for everything else there is Mastercard'
#advertisement='apple innovates relentlessly to make great products , buy an apple'
#advertisement='Biggest thing to happen to Iphone since Iphone'
#advertisement='Be it Monday or Sunday, eat eggs everyday'
#advertisement='Vote for narendra Modi'
#advertisement='Mountain Dew, there is victory after fear'
#advertisement='Washing Powder nirma, nirma'
#advertisement='Android developer needed'
#advertisement='Vote for change . Vote for Kejriwal'
bad_data=False

class TagChunker(nltk.chunk.ChunkParserI):
	def __init__(self, chunk_tagger):
		self._chunk_tagger = chunk_tagger

	def parse(self, tokens):
		# split words and part of speech tags
		(words, tags) = zip(*tokens)
		# get IOB chunk tags
		chunks = self._chunk_tagger.tag(tags)
		# join words with chunk tags
		wtc = itertools.izip(words, chunks)
		# w = word, t = part-of-speech tag, c = chunk tag
		lines = [' '.join([w, t, c]) for (w, (t, c)) in wtc if c]
		# create tree from conll formatted chunk lines
		return nltk.chunk.conllstr2tree('\n'.join(lines))
def conll_tag_chunks(chunk_sents):
	tag_sents = [nltk.chunk.tree2conlltags(tree) for tree in chunk_sents]
	return [[(t, c) for (w, t, c) in chunk_tags] for chunk_tags in tag_sents]

def parse_tree(tree,node_needed,l):
#	print tree.node
	s=[]
	for child in tree:
#		print type(child)
		if(type(child) is not tuple):
#			print '-'*30
			l=parse_tree(child,node_needed,l)
		else:
			if(tree.node==node_needed):
#				tmp=[]
#				tmp.append(child)
#				print 'haha',tmp
				s.append(child)
#			print child
	if s:
		l.append(s)
	return l
def rank_NP(NP_list):
	rated_NP=[]
	for i in NP_list:
		print "NP----:"
		val=0.0
		#val+=1.0*len(i)*.25
		np=[]
		for a,b in i:
			if(b=='JJ' or b=='JJS'):
				val+=1
			elif(b=='NNP' or b=='FW'  or b=='NNPS'):
			 	val+=2
			elif(b=='NN'):
			  	val+=1
			elif(b=="NNS"):
			   val+=1
			print a,b
		np.append(val)
		np.append(i)
		rated_NP.append(tuple(np))
		print np
		print "val is ",val
	rated_NP = sorted(rated_NP, key=lambda tup: tup[0],reverse=True)
	if rated_NP[0][0]==1:
	     global bad_data
	     bad_data=True
	     print "hi----------"
	else:
	     bad_data=False
	print rated_NP
	return rated_NP
def get_chunk(chunk_list):
	chunk=[]
	rank=chunk_list[0][0]
	for c in chunk_list:
		if c[0]>=rank-1 and c[0]!=0:
			print c," geting added"
			for a,b in c[1]:
				for i in a.split(','):
					if i!='':
						print 'appending ',b,i
						chunk.append((b,i))
	return chunk
def get_chunk_element(chunk,element):
	e=[]
	for i in chunk:
		print i
		if i[0] in element  or bad_data:
			e.append(i[1])
	return e
def get_all_elements(chunks,elements):
	print "all elements-------------"
	e=[]
	for a,b in chunks:
		print a,b
		for i in b:
			if i[1] in elements:
				e.append(i[0])
	return e
def rank_wiki_page(page,ngrams):
	title=page.title
	summary=wikipedia.summary(page.title,sentences=9)
	sum_len=len(summary.split())
	val=0.0
	for i in ngrams:
		j=len(i.split())
		if i.lower() in summary.lower():
			val+=len([m.start() for m in re.finditer(i.lower(),summary.lower())])*j
		if i.lower() in title.lower():
			val+=len([m.start() for m in re.finditer(i.lower(),title.lower())])*j*j
	return 1.0*val/sum_len
def get_ngrams():
	add=re.sub('[,.\'\"]','',advertisement)
	add=add.split()
	ngrams=[]
	val=0
	for i in range(1,5):
		for j in range(0,len(add)-i):
			ngram=add[j]
			for k in range(j+1,j+i):
				ngram+=' '+add[k]
			ngrams.append(ngram)
	return ngrams

print "initialization complete"

#advertisement=raw_input('enter sentence')

train = nltk.corpus.conll2000.chunked_sents('train.txt')
test = nltk.corpus.conll2000.chunked_sents('test.txt')
train_chunks = conll_tag_chunks(train)
test_chunks = conll_tag_chunks(test)
u_chunker = nltk.tag.UnigramTagger(train_chunks)
ub_chunker = nltk.tag.BigramTagger(train_chunks, backoff=u_chunker)
chk=TagChunker(ub_chunker)
pos_tagger=POSTagger('./stanford-postagger-full-2014-01-04/models/english-bidirectional-distsim.tagger','./stanford-postagger-full-2014-01-04/stanford-postagger.jar')
tagged=pos_tagger.tag(advertisement.split())

index=0
for i in tagged:
	if i[1]=='FW':
		tagged[index]=(i[0],'NN')
	index+=1
print tagged
tree = chk.parse(tagged)
#print tree
#for subtree in tree.subtrees(filter=lambda t: t.node =='NP'):
# print the noun phrase as a list of part-of-speech tagged words
#	print subtree.leaves()
#print "-"*50
l=[]
l=parse_tree(tree,"NP",l)
print "-"*50
rated_NP=rank_NP(l)
main_np=get_chunk(rated_NP)
print'Main - NP ',main_np
entities=get_chunk_element(main_np,['NN','NNP','NNPS','NNS','JJ' , 'FW','PRP$','PRP'])
print 'Final Entities --',entities
print "Results from wikipedia-------------"
search_query=''
for i in entities:
	search_query+=' '+i
wiki=wikipedia.search(search_query)

ngrams=get_ngrams()
for i in wiki:
	pg=wikipedia.page(i);
	print pg.title
	#print 'Rank----',rank_wiki_page(pg,ngrams)
#print get_all_elements(rated_NP,['NN','NNP','JJ','JJS','FW'])

#for key,value in tagged:
#	print key,value
