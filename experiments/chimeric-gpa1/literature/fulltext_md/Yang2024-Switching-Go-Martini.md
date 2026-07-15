> Source PDF: [docs/papers/pdf/Yang2024-Switching-Go-Martini.pdf](../../../../docs/papers/pdf/Yang2024-Switching-Go-Martini.pdf)
>
> DOI: `10.1021/acs.jctc.3c01222`
>
> Note: local Markdown transcription for reading/search. The PDF above remains the source text authority.

This article is licensed under CC-BY-NC-ND 4.0
|     | pubs.acs.org/JCTC |     |     |     |     |     |     |     |     |     |     |     |     |     | Article |
| --- | ----------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ------- |
Switching Go‑Martini for Investigating Protein Conformational
̅
|     | Transitions |     |     |     | and | Associated |     |     | Protein−Lipid |     | Interactions |     |     |     |     |
| --- | ----------- | --- | --- | --- | --- | ---------- | --- | --- | ------------- | --- | ------------ | --- | --- | --- | --- |
Song*
|                                                                                                         | Song          | Yang                                           | and         | Chen           |                |                |              |              |            |                        |     |     |     |                       |     |
| ------------------------------------------------------------------------------------------------------- | ------------- | ---------------------------------------------- | ----------- | -------------- | -------------- | -------------- | ------------ | ------------ | ---------- | ---------------------- | --- | --- | --- | --------------------- | --- |
|                                                                                                         |               | CiteThis:J.Chem.TheoryComput.2024,20,2618−2629 |             |                |                |                |              |              |            | ReadOnline             |     |     |     |                       |     |
|                                                                                                         | ACCESS        |                                                |             |                |                |                |              |              |            |                        |     |     | *   |                       |     |
|                                                                                                         |               |                                                |             |                | Metrics&More   |                |              |              |            | ArticleRecommendations |     |     | sı  | SupportingInformation |     |
| .selcitra dehsilbup erahs yletamitigel ot woh no snoitpo rof senilediuggnirahs/gro.sca.sbup//:sptth eeS | ABSTRACT:     |                                                | Proteins    |                | are dynamic    |                | biomolecules | that         | can        | trans-                 |     |     |     |                       |     |
|                                                                                                         | form          | between                                        |             | different      | conformational |                |              | states when  | exerting   |                        |     |     |     |                       |     |
|                                                                                                         | physiological |                                                | functions,  |                | which          | is difficult   |              | to simulate  | using      | all-                   |     |     |     |                       |     |
|                                                                                                         | atom          | methods.                                       |             | Coarse-grained |                | (CG)           | Go̅-like     | models       | are widely |                        |     |     |     |                       |     |
|                                                                                                         | used          | to                                             | investigate | large-scale    |                | conformational |              | transitions, |            | which                  |     |     |     |                       |     |
.)CTU( 85:61:40 ta 6202 ,5 yluJ no 722.222.712.712 aiv dedaolnwoD
|     | usually | adopt |     | implicit | solvent | models |     | and therefore | cannot |     |     |     |     |     |     |
| --- | ------- | ----- | --- | -------- | ------- | ------ | --- | ------------- | ------ | --- | --- | --- | --- | --- | --- |
explicitlycapturetheinteractionbetweenproteinsandsurrounding
|     | molecules, |                | such  | as water  | and         | lipid molecules. |     | Here,       | we present  | a     |     |     |     |     |     |
| --- | ---------- | -------------- | ----- | --------- | ----------- | ---------------- | --- | ----------- | ----------- | ----- | --- | --- | --- | --- | --- |
|     | new        | method,        | named | Switching |             | Go̅-Martini,     |     | to simulate | large-scale |       |     |     |     |     |     |
|     | protein    | conformational |       |           | transitions | between          |     | different   | states,     | based |     |     |     |     |     |
ontheswitchingGo̅methodandtheCGMartini3forcefield.The
method is straightforward and efficient, as demonstrated by the benchmarking applications for multiple protein systems, including
glutamine binding protein (GlnBP), adenylate kinase (AdK), and β -adrenergic receptor (β2AR). Moreover, by employing the
2
SwitchingGo̅-Martinimethod,wecannotonlyunveiltheconformationaltransitionfromtheE2Pi-PLstatetoE1stateofthetype4
P-type ATPase (P4-ATPase) flippase ATP8A1-CDC50 but also provide insights into the intricate details of lipid transport.
|     | 1.  | INTRODUCTION |     |     |     |     |     |     |     |     |     |     |     |     |     |
| --- | --- | ------------ | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
fullconformationalchangesofproteinsatatomicresolution.To
Proteinsperformavastvarietyoffundamentalfunctionsinliving alleviatethedetaillossinwetexperiments,moleculardynamics
(MD)simulationhasbeenthemostwidelyusedcomputational
|     | systems,including |     |     | catalyzing |     | enzymaticreactions, |     | signal | trans- |     |     |     |     |     |     |
| --- | ----------------- | --- | --- | ---------- | --- | ------------------- | --- | ------ | ------ | --- | --- | --- | --- | --- | --- |
methodforrevealingthetransitionpathsofproteins.All-atom
|     | duction, |     | and transporting |     | molecules. |     | During | most | of these |     |     |     |     |     |     |
| --- | -------- | --- | ---------------- | --- | ---------- | --- | ------ | ---- | -------- | --- | --- | --- | --- | --- | --- |
processes, proteins need to change their structures to MDsimulationsareoftenlimitedtothemicrosecondtimescale,
dynamically adapt to their functions. For example, enzymes so a variety of enhanced sampling methods are developed to
enclose the catalytic pockets to catalyze the reactions after acceleratetheexplorationofproteintransitions,suchasreplica
bindingtothesubstrates.1,2Mechanicallyactivatedionchannels exchange,9 metadynamics,10 and umbrella sampling.11 In
canopentheporestoallowionspassingthroughthemembrane addition, the Markov state model is often utilized to sample
whensensingtheincreaseofsurfacetension.3Gprotein-coupled the transition paths of protein conformational changes.12
receptors (GPCRs) sense the binding of small molecules Nonetheless, it is still challenging to sample the large-scale
|     | followed |     | by the | conformational |     | changes |     | of the sixth | trans- |                |             |     |              |     |               |
| --- | -------- | --- | ------ | -------------- | --- | ------- | --- | ------------ | ------ | -------------- | ----------- | --- | ------------ | --- | ------------- |
|     |          |     |        |                |     |         |     |              |        | conformational | transitions |     | of proteins, | and | the expensive |
membrane helix to induce the G protein binding and signal computational cost does not allow for high-throughput
transduction.4
|     |     |     | Thus, | proteins |     | in living | organisms | need | to be | applications. |     |     |     |     |     |
| --- | --- | --- | ----- | -------- | --- | --------- | --------- | ---- | ----- | ------------- | --- | --- | --- | --- | --- |
dynamictoundergoconformationaltransitionstoperformtheir Apotentialsolutionistheuseofcoarse-grained(CG)force
functions.
fields,whichreducesthecomputationalcostbyunitinggroups
Theconformationalchangesofproteinscanbemonitoredby
ofatomsintoeffectiveinteractionsites,resultinginasubstantial
super-resolution experimental methods and computational computational speed-up.13−18 One of the most popular CG
simulationmethods.Thestructuralbiologymethods,including methodsistheGo̅-likemodel,whichgroupsoneresidueormore
|     | X-ray | crystallography, |     |     | nuclear | magnetic | resonance, |     | and cryo- |             |           |              |     |             |             |
| --- | ----- | ---------------- | --- | --- | ------- | -------- | ---------- | --- | --------- | ----------- | --------- | ------------ | --- | ----------- | ----------- |
|     |       |                  |     |     |         |          |            |     |           | to a pseudo | atom with | Lenard-Jones |     | potentialto | maintainthe |
electronmicroscopy(cryo-EM),canprimarilycapturethemost
|     |     |     |     |     |     |     |     |     |     | second and | higher | structures.19 | These | methods | have obtained |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---------- | ------ | ------------- | ----- | ------- | ------------- |
populated,ensemble-averagedstructures,althougheffortshave
|     | been          | made | to  | uncover | the     | high-energy, |     | low-populated   |     |           |             |      |     |     |     |
| --- | ------------- | ---- | --- | ------- | ------- | ------------ | --- | --------------- | --- | --------- | ----------- | ---- | --- | --- | --- |
|     |               |      |     |         |         | dynamics.5−7 |     |                 |     | Received: | November3,  | 2023 |     |     |     |
|     | conformations |      |     | during  | protein |              |     | Single-molecule |     |           |             |      |     |     |     |
|     |               |      |     |         |         |              |     |                 |     | Revised:  | February22, | 2024 |     |     |     |
technologieshavealsobeenusedtocharacterizetheconforma-
tional transitions of proteins, such as single-molecule Förster Accepted: February22, 2024
resonance energy transfer and single-molecule force spectros- Published: March6, 2024
copy.8
|     |     | However, |     | these | methods | merely |     | capture some | low- |     |     |     |     |     |     |
| --- | --- | -------- | --- | ----- | ------- | ------ | --- | ------------ | ---- | --- | --- | --- | --- | --- | --- |
dimensionalcharacteristicsofproteinsandcannotdescribethe
©2024TheAuthors.Publishedby
AmericanChemicalSociety https://doi.org/10.1021/acs.jctc.3c01222
|     |     |     |     |     |     |     |     |     |     | 2618 |     |     | J.Chem.TheoryComput.2024,20,2618−2629 |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---- | --- | --- | ------------------------------------- | --- | --- |

JournalofChemicalTheoryandComputation pubs.acs.org/JCTC Article
Figure1.SwitchingGo̅-MartinisimulationforGlnBP.(a)SchematicoftheswitchingGo̅-Martiniapproach.Theenergylandscapesaresimplifiedas
quadratic curves (blue and red), and the protein state is drawn as a ball (brown). (b,c) CG structures of GlnBP in the open and closed state,
respectively.(d)rmsdofGlnBPduringthesimulations,withrespecttotheopen-(red)orclosed-state(blue)structures.Thesolidlinescorrespondto
the average values obtained from 50 independent simulation trajectories, while the shaded area represents the standard deviation. (e) Distance
betweenthebackboneatomsofT59andT130duringtheswitchingGo̅-Martinisimulations.Thesolidlinerepresentstheaveragevalue,similarto(d),
andtheshadedarearepresentsthestandarddeviation.Theredandbluedashedlinesrepresentthereferencedistancefromtheopen-andclosed-state
structures.
great success in simulating the conformational changes of processoflipidtranslocationfromtheexoplasmicleaflettothe
glutamine-binding protein,20 adenylate kinase (AdK),21,22 cytoplasmic leaflet was successfully simulated, which was
molecularmotorprotein,23andsoon.However,thelackofan facilitated by conformational transitions of the protein. Our
explicitsolventenvironmentandbiomembraneinthesemodels resultsdemonstratethat,withtheSwitchingGo̅-Martinimethod,
may impede the system from accurately simulating the actual one cannot merely efficiently sample the potential conforma-
dynamic process of membrane proteins, especially when the tionaltransitionpathsofproteinsbutalsogaininsightsintothe
interactionsofproteinsandlipidsarecrucial,whichisoftenthe interactionsbetweendynamicproteinsandlipids.
case.
| The Martini  | force         | field | is one          | of the most | widely | used CG      | 2. RESULTS          |     |             |     |     |        |          |
| ------------ | ------------- | ----- | --------------- | ----------- | ------ | ------------ | ------------------- | --- | ----------- | --- | --- | ------ | -------- |
| force fields | in simulating |       | the interaction | between     |        | proteins and |                     |     |             |     |     |        |          |
|              |               |       |                 |             |        |              | 2.1. Conformational |     | Transitions |     | of  | GlnBP, | AdK, and |
lipids.24,25However,thisforcefieldwashardlyusedtosimulate
|                        |     |     |         |         |              |          | β2AR. The | switching  | method    | is  | a straightforward |            | way to |
| ---------------------- | --- | --- | ------- | ------- | ------------ | -------- | --------- | ---------- | --------- | --- | ----------------- | ---------- | ------ |
| protein conformational |     |     | changes | because | the previous | versions |           |            |           |     |                   |            |        |
|                        |     |     |         |         |              |          | transform | the energy | landscape | of  | one state         | of protein | to the |
utilized the elastic network potential, which hindered large other, which has been extensively utilized in previous
adapted.26
| conformational      | changes  |           | to occur | unless  | heavily      |             | studies.23,30−32 |                  |           |           |        |                |             |
| ------------------- | -------- | --------- | -------- | ------- | ------------ | ----------- | ---------------- | ---------------- | --------- | --------- | ------ | -------------- | ----------- |
|                     |          |           |          |         |              |             |                  | The              | schematic | in        | Figure | 1a illustrates | the         |
| Recently,           | Go̅-like | Martini   | models,  | which   | used contact | map-        |                  |                  |           |           |        |                |             |
|                     |          |           |          |         |              |             | mechanism        | of the switching |           | approach. |        | While          | the protein |
| based Lennard-Jones |          | potential |          | network | to replace   | the elastic |                  |                  |           |           |        |                |             |
oscillatesintheenergywellAwiththeenergylandscapeofState
network, showed very promising results in studying protein A, we manually switch the energy landscape of the protein to
dynamics.27,28Particularly,theworkbyPomaetal.openedthe
|             |               |     |             |                |     |         | that of State | B. After    | that, theprotein |     | structure  | of  | State Ahas  |
| ----------- | ------------- | --- | ----------- | -------------- | --- | ------- | ------------- | ----------- | ---------------- | --- | ---------- | --- | ----------- |
| possibility | of simulating |     | large-scale | conformational |     | changes |               |             |                  |     |            |     |             |
|             |               |     |             |                |     |         | high energy   | and becomes | unstable.        |     | Gradually, | the | protein can |
usingMartini-likeforcefields.27WithMartini3released,25the
changeitsconformationtofallintotheenergywellB.Thedetails
Lennard-Jonespotentialbecameoneoftheoptionalinteraction
oftheimplementationcanbefoundinthesectionofMaterials
networkstostabilizeproteinstructures,anditwasdemonstrated and Methods. To validate the approach, we tested it in three
that the switching approach can be utilized to study small well-studiedbenchmarkingsystems,includingGlnBP,AdK,and
| molecularswitches.29Therefore,itappearsthatthecombination |     |          |       |          |         |               | β2AR.  |              |     |        |                         |     |     |
| --------------------------------------------------------- | --- | -------- | ----- | -------- | ------- | ------------- | ------ | ------------ | --- | ------ | ----------------------- | --- | --- |
| of the Switching                                          |     | Go̅-like | model | with the | Martini | 3 force field |        |              |     |        |                         |     |     |
|                                                           |     |          |       |          |         |               | 2.1.1. | GlnBP. GlnBP | is  | one of | the periplasmic-binding |     |     |
maycarryagreatpotentialinsimulatingconformationalchanges proteins, which assists L-glutamine uptake in bacteria.1 The
of multiple-state proteins, similar to the previous Go̅ crystal structures of GlnBP were resolved with a ligand-bound
models,19,20butwithexplicitsurroundingmolecules. closedstateandaligand-freeopenstate(Figure1b,c).33,34Inthe
Inthisstudy,wepresentthattheswitchingapproachforthe
holostate,glutamineissurroundedbytwoglobaldomains(large
Go̅-like Martini model can indeed be used to simulate domain and small domain) connected by a linker. Both the
conformational changes of proteins and sample the transition experimental tests and simulation models have revealed the
pathwithhighaccuracyandafastspeed.Weutilizedthreewell- open−closed transition of GlnBP during the glutamine
tested proteins, GlnBP, AdK, and β -adrenergic receptor associatinganddisassociatingprocess.35−37
2
(β2AR),
to benchmark the accuracy of the method. Then, we We used the switching Go̅-Martini approach to simulate 50
appliedthemethodtoinvestigatethelipidtransportmechanism independent repeats of the conformational changes of GlnBP
of phosphatidylserine (PS) flippase ATP8A1-CDC50a. The fromopentoclosedandbacktotheopenstateinoursystem.
|     |     |     |     |     |     | 2619 |     |     |     |     | https://doi.org/10.1021/acs.jctc.3c01222 |     |     |
| --- | --- | --- | --- | --- | --- | ---- | --- | --- | --- | --- | ---------------------------------------- | --- | --- |
J.Chem.TheoryComput.2024,20,2618−2629

JournalofChemicalTheoryandComputation pubs.acs.org/JCTC Article
| The root-mean-square |     |      | deviation | (rmsd)             | of  | the CG | backbone   |     |     |     |     |     |     |
| -------------------- | --- | ---- | --------- | ------------------ | --- | ------ | ---------- | --- | --- | --- | --- | --- | --- |
| (BB) atoms           | was | used | to show   | the conformational |     |        | changes of |     |     |     |     |     |     |
GlnBPduringoursimulations.AsshowninFigure1d,theresults
of50independentsimulationsshowedthattheconformationof
GlnBPchangedalongtheexpectedtransitionpathwaywhenwe
| switched    | on the | open-  | or closed-energy |                   | landscapes |        | of GlnBP. |     |     |     |     |     |     |
| ----------- | ------ | ------ | ---------------- | ----------------- | ---------- | ------ | --------- | --- | --- | --- | --- | --- | --- |
| The opening |        | extent | of the           | substrate-binding |            | pocket | was       |     |     |     |     |     |     |
measuredbythedistancebetweentheBBatomsofT59(large
domain)andT130(smalldomain).Asexpected,thedistancein
thesimulationsdecreasedaftertheclosedstatewasswitchedon
andincreasedwhentheopenstatewasswitchedon(Figure1e).
| These findings |            | demonstrate |          | that the    | switching | Go̅-Martini    |     |     |     |     |     |     |     |
| -------------- | ---------- | ----------- | -------- | ----------- | --------- | -------------- | --- | --- | --- | --- | --- | --- | --- |
| method         | can indeed | be          | utilized | to simulate | the       | conformational |     |     |     |     |     |     |     |
transitionsbetweentwodistinctstates.
| To further  | demonstrate |     | the            | robustness | of         | the approach, | a         |     |     |     |     |     |     |
| ----------- | ----------- | --- | -------------- | ---------- | ---------- | ------------- | --------- | --- | --- | --- | --- | --- | --- |
| continuous  | simulation  |     | comprising     | 10         | cycles     | of open       | ↔closed   |     |     |     |     |     |     |
| transitions | of GlnBP    |     | was performed. |            | Throughout |               | the simu- |     |     |     |     |     |     |
lation,boththermsdanddistanceofT59−T130changedwith
| the open | or closed | state | switched |     | on or off | (Figure | S1a,b). |     |     |     |     |     |     |
| -------- | --------- | ----- | -------- | --- | --------- | ------- | ------- | --- | --- | --- | --- | --- | --- |
Moreover,themetricsassociatedwiththeopenorclosedstate
| remained        | stable | and consistent |     | during | the simulations. |     | These      |     |     |     |     |     |     |
| --------------- | ------ | -------------- | --- | ------ | ---------------- | --- | ---------- | --- | --- | --- | --- | --- | --- |
| results support |        | the robustness |     | of our | method           | in  | simulating |     |     |     |     |     |     |
repetitiveconformationaltransitionsbetweendistinctstates.
| 2.1.2. | AdK. AdK | is  | a ubiquitous |     | enzyme | that catalyzes | the |     |     |     |     |     |     |
| ------ | -------- | --- | ------------ | --- | ------ | -------------- | --- | --- | --- | --- | --- | --- | --- |
reversiblephosphoryltransferofAMPandATPintotwoADP,
whichisimportantincellularenergyhomeostasis.2AdKconsists
| of the ATP-binding |         |           | domain | (LID),  | AMP-binding |       | domain   |     |     |     |     |     |     |
| ------------------ | ------- | --------- | ------ | ------- | ----------- | ----- | -------- | --- | --- | --- | --- | --- | --- |
| (NMP),             | and the | remainder |        | linking | them        | named | the Core |     |     |     |     |     |     |
domain.Thecrystalstructuresoftheclosedandtheopenstates Figure 2. Switching Go̅-Martini simulation for AdK. (a−d)
| of AdK | in Figure | 2a,b | show | that the | LID | and NMP | remain |                |               |            |                |        |      |
| ------ | --------- | ---- | ---- | -------- | --- | ------- | ------ | -------------- | ------------- | ---------- | -------------- | ------ | ---- |
|        |           |      |      |          |     |         |        | Representative | structures of | four major | conformational | states | with |
closed when binding to ATP and AMP while exposing their NMPandLIDopenorclosed.NMPdomain(residues31−60),LID
bindingpocketsintheunboundstate.38,39Theconformational domain(residues127−164),andtheremainderarecoloredskyblue,
transition of AdK between the open and closed states is salmon, and tan, respectively. (e,f) Two-dimension conformational
|            |     |               |     |         |       |          |        | transition                         | paths (NMP-closing | pathway, | left; LID-closing |     | pathway, |
| ---------- | --- | ------------- | --- | ------- | ----- | -------- | ------ | ---------------------------------- | ------------------ | -------- | ----------------- | --- | -------- |
| frustrated | and | in a stepwise |     | manner, | which | has been | widely |                                    |                    |          |                   |     |          |
|            |     |               |     |         |       |          |        | right)areconstructedwithtwoanglesθ |                    |          | andθ              |     |          |
studied by previous experiments and computational simula- NMP LID asthereaction
tions.21,22,40 There are two major kinetic pathways found: the coordinates.Thecolorofthecirclesdecreasesalongwiththesimulation
|     |     |     |     |     |     |     |     | time. The | cyan triangle, diamond, | and square | represent | the | closed, |
| --- | --- | --- | --- | --- | --- | --- | --- | --------- | ----------------------- | ---------- | --------- | --- | ------- |
NMP-closingpathwayandtheLID-closingpathway.TheNMP-
intermediate,andopenstatesofAdK.
closingpathwayischaracterizedbytheintermediatestructurein
whichtheNMPremainsclosedandLIDopen(Figure2c),while
intheLID-closingpathwaytheNMPdomainisopenandLID signalintothecell,playingimportantrolesinmusclerelaxation,
| closed(Figure2d). |     |     |     |     |     |     |     |               |             | secretion.4,45 |     |            |     |
| ----------------- | --- | --- | --- | --- | --- | --- | --- | ------------- | ----------- | -------------- | --- | ---------- | --- |
|                   |     |     |     |     |     |     |     | vasodilation, | and insulin |                | The | activation | and |
We used the switching Go̅-Martini method to search the deactivation mechanisms of β2AR have been experimentally
above pathways in 70 independent closed-to-open MD well studied, in which the snapshots of the inactive and active
simulations, starting with the closed structure. The rmsd of stateβ2ARstructures(Figure3a,b)havebeencharacterizedby
AdK showed that conformational changes occurred when we the X-ray method.46,47 However, the detailed conformational
| switchedontheopen-stateenergylandscape(FigureS2a).We |     |     |     |     |     |     |     |            |                | β2AR       |     |                  |     |
| ---------------------------------------------------- | --- | --- | --- | --- | --- | --- | --- | ---------- | -------------- | ---------- | --- | ---------------- | --- |
|                                                      |     |     |     |     |     |     |     | transition | pathway of the | activating |     | and deactivating |     |
used two angles θ and θ as reaction coordinates to processremainedelusive.Therefore,micro-tomilli-secondsall-
|     |     | NMP |     | LID |     |     |     |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
characterize the state of the ensembles during our simulations atom simulations were conducted to reveal the activation and
(Figures 2e,f and S2b−f). The analysis of the conformational deactivation mechanism of β2AR,48,49 which provided a solid
changes revealed that the LID domain and the NMP domain basisforbenchmarkingGo̅-likeCGsimulations.
underwentagradualopeningduringthetransitionprocess.Both We used the switching Go̅-Martini method to simulate the
theNMP-closingpathwayandLID-closingpathwaywerefound deactivation process of β2AR for 40 independent repeats and
inourswitchingGo̅-Martinisimulations,andtheNMP-closing compared our results with those from previous studies. The
pathwaywasdominantwithaprobabilityof68.6%,comparedto rmsd of BB atoms showed that the conformational transitions
10%alongtheLID-closingpathway(FigureS2d,e).Ourresults took place after we switched on the energy landscape of the
inactivestateofβ2AR(FigureS3a).Toaccuratelyanalyzethe
| for AdK’s | NMP-closing |     | pathway |     | are consistent |     | with the |     |     |     |     |     |     |
| --------- | ----------- | --- | ------- | --- | -------------- | --- | -------- | --- | --- | --- | --- | --- | --- |
previouscomputationalstudiesbyLuandWang,Lietal.,and conformationaltransitionpath,thedistancebetweenhelix6and
Stilleretal.21,41,42However,itisnoteworthythattherearealso helix 3 (measured between residues R131 and L272) and the
papers reporting the LID-closing intermediate to be more rmsdoftheNPxxYmotifinhelix7withrespecttotheinactive
stable.43,44 structure were utilized as the reaction coordinates. Figure 3c
2.1.3. β2AR. showsthatthehelix6−helix3distancewas14.0±0.6Åinthe
|     |     | The third | benchmark |     | is the | deactivation | of  |     |     |     |     |     |     |
| --- | --- | --------- | --------- | --- | ------ | ------------ | --- | --- | --- | --- | --- | --- | --- |
β2AR,amemberofthetransmembraneproteinfamilyofGPCR. activestateandgraduallydecreasedto9.4±0.5Å,whichwas
β2AR functions by binding to adrenaline and transducing the within the range of the inactive state. The rmsd of the NPxxY
|     |     |     |     |     |     |     | 2620 |     |     | https://doi.org/10.1021/acs.jctc.3c01222 |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | ---- | --- | --- | ---------------------------------------- | --- | --- | --- |
J.Chem.TheoryComput.2024,20,2618−2629

JournalofChemicalTheoryandComputation pubs.acs.org/JCTC Article
Figure3.SwitchingGo̅-Martinisimulationforβ2AR.(a,b,d)RepresentativeCGstructuresofβ2ARintheinactive,active,andintermediatestates
embeddedintothePOPCbilayer,respectively.Theproteinisshownasthetanribbon,theNPxxYmotifiscoloredorange,andtheBBofR131and
L272arecoloredsky-bluewithspherestyle.ThePOPCmembraneisshownasgraysurfaces.(c)Two-dimensionconformationaltransitionpathway,
asconstructedwiththehelix6−helix3distanceandthermsdofNPxxYmotifwithrespecttotheinactivestate.Theredcolorofthecirclesdecreases
alongwiththesimulationtime.Thecyansquare,diamond,andtrianglerepresenttheactive,intermediate,andinactivestatesofβ2AR.
| motif changed | and | was finally | close | to the | inactive structure. |     |     |     |     |
| ------------- | --- | ----------- | ----- | ------ | ------------------- | --- | --- | --- | --- |
UnliketheconformationalchangesofAdKduringthecatalysis,
| β2AR mainly | underwent |     | a single | pathway | during | the |     |     |     |
| ----------- | --------- | --- | -------- | ------- | ------ | --- | --- | --- | --- |
deactivationprocess,inwhichthermsdofNPxxYfirstdecreased
andtheintracellularendofhelix6graduallyshiftedtowardhelix
| 3 (Figures | 3c,d and | S3b,c). | Only one | rare pathway | was | found |     |     |     |
| ---------- | -------- | ------- | -------- | ------------ | --- | ----- | --- | --- | --- |
withinour40simulations,inwhichtheorderofconformational
transitionsonthetworeactioncoordinateswasreversed(Figure
S3d).Alltheseobservationswereconsistentwiththeunbiased
all-atomMDsimulationsusingthespecializedsupercomputers
Anton.48
| 2.1.4. Benchmark |             | Summary.      | We   | utilized       | three well-tested |     |     |     |     |
| ---------------- | ----------- | ------------- | ---- | -------------- | ----------------- | --- | --- | --- | --- |
| examples         | including   | GlnBP,        | AdK, | and β2AR       | to examine        | the |     |     |     |
| switching        | Go̅-Martini | method.       | The  | results        | show that         | the |     |     |     |
| approach         | cannot      | only simulate | the  | conformational | changes           | of  |     |     |     |
proteinbetweendifferentstatesinthepresenceofexplicitwater
andlipidmoleculesbutalsorevealthetransitionpathwaysthat
arequalitativelyconsistentwithpreviousCGandall-atomMD
simulations.
| 2.2. New | Case | Study: | Lipid | Transport | through |     |     |     |     |
| -------- | ---- | ------ | ----- | --------- | ------- | --- | --- | --- | --- |
Flippase ATP8A1-CDC50a. After validating the method, we Figure 4. Switching Go̅-Martini simulations for ATP8A1-CDC50a.
(a,b,d)RepresentativeCGstructuresofATP8A1-CDC50aintheE2Pi-
usedittoinvestigatetheconformationaltransitionsaswellasthe
|              |       |           |         |     |                    | PL, E1, and intermediate | states embedded | into the | lipid bilayer, |
| ------------ | ----- | --------- | ------- | --- | ------------------ | ------------------------ | --------------- | -------- | -------------- |
| accompanying | lipid | transport | process | of  | the lipid flippase |                          |                 |          |                |
respectively.Theproteinisshownasthetanribbon.TheA,N,andP
ATP8A1-CDC50acomplex.ATP8A1isoneoftheP4-ATPases,
domainsofATP8A1arelabeledandcoloredgold,deeppink,andsky
whichfunctionswiththeregulatoryproteinCDC50aasthelipid
blue,respectively.Thetwohelicesconstructingthewindowofthelipid-
flippase,translocatingthePSlipidsfromtheexoplasmicleafletof binding pocket are colored light green and CDC50a is colored light
the plasma membrane to the cytoplasmic leaflet (lipid gray. The membrane is shown as gray surfaces. (c) Two-dimension
flipping).50,51 Like other P-type ATPases, P4-ATPases go conformationaltransitionpathway,asconstructedwiththedistanceof
through the Post-Albers cycle including E1, E1-ATP, E1P- A−Pdomainsandthewidthofthelipid-bindingpocket.Thebluecolor
ofthecirclesdecreasesalongwiththesimulationtime.Thecyansquare,
| ADP, E1P, | E2P, | and E2Pi-PL | states | during | the lipid flipping |     |     |     |     |
| --------- | ---- | ----------- | ------ | ------ | ------------------ | --- | --- | --- | --- |
process.52−54 diamond,andcirclerepresenttheE2Pi-PL,intermediate,andE1states
|     | Among | these | states, | the lipid | translocation | is  |     |     |     |
| --- | ----- | ----- | ------- | --------- | ------------- | --- | --- | --- | --- |
ofATP8A1-CDC50a.
mainlycoupledtothetransitionsofE2Pi-PL-to-E1stateswith
phosphatereleaseatthePdomainofP4-ATPases.Althoughthe
cryo-EMstructuresofthesestateshavebeenobtained(Figure
4a,b), the exquisite details of the conformational transitions Thus,weutilizedtheswitchingGo̅-Martiniapproachtosimulate
revealed.52−54
between these functional states have not been the E2Pi-PL-to-E1 conformationaltransitions of the ATP8A1-
|     |     |     |     |     |     | 2621 | https://doi.org/10.1021/acs.jctc.3c01222 |     |     |
| --- | --- | --- | --- | --- | --- | ---- | ---------------------------------------- | --- | --- |
J.Chem.TheoryComput.2024,20,2618−2629

JournalofChemicalTheoryandComputation pubs.acs.org/JCTC Article
| CDC50a | complex | and | investigated |     | the lipid | flipping | process |     |     |     |     |     |     |     |     |
| ------ | ------- | --- | ------------ | --- | --------- | -------- | ------- | --- | --- | --- | --- | --- | --- | --- | --- |
duringtheconformationalchanges.
| 2.2.1.         | E2Pi-PL-to-E1 |       | Conformational  |           |               | Transitions | of      |     |     |     |     |     |     |     |     |
| -------------- | ------------- | ----- | --------------- | --------- | ------------- | ----------- | ------- | --- | --- | --- | --- | --- | --- | --- | --- |
| ATP8A1-CDC50a. |               | The   | CG model        | of        | the P4-ATPase |             | complex |     |     |     |     |     |     |     |     |
| in the E2Pi-PL |               | state | was constructed |           | and           | embedded    | into an |     |     |     |     |     |     |     |     |
| asymmetric     | membrane,     |       | with            | POPS      | occupying     | 10%         | of the  |     |     |     |     |     |     |     |     |
| cytoplasmic    | leaflet       | and   | POPC            | occupying | the           | remaining   | lipid   |     |     |     |     |     |     |     |     |
bilayer(Figure4a).ThePSlipidfoundinthebindingpocketof
| ATP8A1 | in the | EM  | density | map | was also | retained | and |     |     |     |     |     |     |     |     |
| ------ | ------ | --- | ------- | --- | -------- | -------- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
transformedintothePOPSCGmodel.A200nssimulationof
ATP8A1-CDC50aintheE2Pi-PLstatewasperformedfollowed
byswitchingtotheE1statewithasimulationof800ns.Totally
50independentconformationaltransitionswereobtained,and
| rmsd of   | the complex |       | during   | the main | transition | processes | is         |     |     |     |     |     |     |     |     |
| --------- | ----------- | ----- | -------- | -------- | ---------- | --------- | ---------- | --- | --- | --- | --- | --- | --- | --- | --- |
| shown in  | Figure      | S4a.  | The rmsd | with     | respect    | to the    | E1 state   |     |     |     |     |     |     |     |     |
| decreased | from        | 7.6 ± | 0.6 to   | 4.6      | ± 0.7 Å    | after     | the switch |     |     |     |     |     |     |     |     |
operation,andmeanwhile,thevaluewithrespecttotheE2Pi-PL
|                 |      |          | ±         |            | ±           |        |            |     |     |     |     |     |     |     |     |
| --------------- | ---- | -------- | --------- | ---------- | ----------- | ------ | ---------- | --- | --- | --- | --- | --- | --- | --- | --- |
| state increased |      | from 3.6 | 0.6       | to 7.0     | 0.6         | Å. The | changes in |     |     |     |     |     |     |     |     |
| rmsd along      | with | the      | switching | simulation | illustrated |        | that the   |     |     |     |     |     |     |     |     |
E2Pi-PLstateofATP8A1-CDC50awassuccessfullyswitchedto
theE1state.
| In a      | cell, the | E2Pi-PL-to-E1 |       | transition |           | is facilitated | by         |     |     |     |     |     |     |     |     |
| --------- | --------- | ------------- | ----- | ---------- | --------- | -------------- | ---------- | --- | --- | --- | --- | --- | --- | --- | --- |
| phosphate | release   | at            | the P | domain     | of ATP8A1 |                | with the A |     |     |     |     |     |     |     |     |
domainfarawayfromit.Inthisprocess,thelipid-bindingpocket
ofATP8A1closes,andtheboundPSlipidcanbetranslocated
| from the         | exoplasmic |       | leaflet | to the   | cytoplasmic | leaflet | of the      |     |     |     |     |     |     |     |     |
| ---------------- | ---------- | ----- | ------- | -------- | ----------- | ------- | ----------- | --- | --- | --- | --- | --- | --- | --- | --- |
| plasma membrane. |            | Thus, | the     | distance | between     | the     | A domain    |     |     |     |     |     |     |     |     |
| and the          | P domain   | of    | ATP8A1  | and      | the width   | of      | the binding |     |     |     |     |     |     |     |     |
pocketwereusedasreactioncoordinatestomonitortheE2Pi- Figure 5. Lipid translocation and lipid-binding sites of ATP8A1-
PL-to-E1 conformational transitions of ATP8A1-CDC50a. As CDC50a.(a)Traces(left)anddistributiondensity(right)ofthelipid
showninFigures4c,dandS5,thewidthofthebindingpocket, heads across the z-axis in the course of simulations. All lipids
|          |        |          |         |     |         |           | 100− | successfully | translocated |         | in our | 50 simulations | are  | shown           | as solid |
| -------- | ------ | -------- | ------- | --- | ------- | --------- | ---- | ------------ | ------------ | ------- | ------ | -------------- | ---- | --------------- | -------- |
| measured | as the | distance | between | two | helices | (residues |      |              |              |         |        |                |      |                 |          |
|          |        |          |         |     |         |           |      | lines with   | different    | colors. | Red    | and blue       | dash | lines represent | the      |
104and878−883),firstdecreasedfrom14.0±0.4to9.8±0.2
|     |     |     |     |     |     |     |     | exoplasmic | and | cytoplasmic | leaflets | of the | bilayer | membrane. | The |
| --- | --- | --- | --- | --- | --- | --- | --- | ---------- | --- | ----------- | -------- | ------ | ------- | --------- | --- |
Å.Then,thedistanceofA−Pdomainshadasignificantincrease
positionsoflipid-bindingsites(LBS1andLBS2)arealsolabeled.(b,c)
| from 32.6    | ±   | 0.3 to | 39.6 ± | 0.4 Å.     | Upon  | analyzing | all 50     |               |       |     |         |               |     |                |     |
| ------------ | --- | ------ | ------ | ---------- | ----- | --------- | ---------- | ------------- | ----- | --- | ------- | ------------- | --- | -------------- | --- |
|              |     |        |        |            |       |           |            | Lipid-binding | sites | for | E2Pi-PL | and E1 states | of  | ATP8A1-CDC50a, |     |
| simulations, | we  | found  | that   | 36 repeats | (72%) |           | out of our |               |       |     |         |               |     |                |     |
respectively.Theproteincomplexisshownasthetanribbon,withthe
simulations followed the aforementioned pathway, while a helicesformingthewindowofthelipid-bindingpocketcoloredlight
distinct conformational transition was observed in five repeats green.Lipid-bindingsitesareshownasthemeshrepresentation.(d,e)
(10%),inwhichthelipid-bindingpocketunderwentclosureand Polarresiduesaroundlipid-bindingsite 1and2forE2Pi-PLandE1
theAdomain simultaneouslymovedaway from thePdomain states of ATP8A1-CDC50a, respectively.TheBB atoms ofthe polar
(FigureS4a−d).Therestninerepeats(18%)appearedtofollow residuesareshownasdodgerbluespheres.
| the first | pathway | but | were | incomplete | and | remained | in the |     |     |     |     |     |     |     |     |
| --------- | ------- | --- | ---- | ---------- | --- | -------- | ------ | --- | --- | --- | --- | --- | --- | --- | --- |
intermediatestateinoursimulationtime(FigureS4e,f),possibly Pearson correlation coefficient analysis. As shown in Figure
duetothelimitedsimulationtime. S7a,thecorrelationcoefficientsbetweentheclosingofthelipid-
2.2.2.LipidTranslocationMechanismofATP8A1-CDC50a. binding pocket, the movement of the A−P domains, and the
| Alongwiththeconformationaltransition,adetailedanalysisof |     |     |     |     |     |     |     |                |     |         |           |        |         | −1, |       |
| -------------------------------------------------------- | --- | --- | --- | --- | --- | --- | --- | -------------- | --- | ------- | --------- | ------ | ------- | --- | ----- |
|                                                          |     |     |     |     |     |     |     | lipid flipping |     | process | exhibited | values | near +1 | or  | which |
thelipid translocation processwas conducted. In 23 outof 50 indicates a high degree of synchronicity among these three
independent simulations, lipid translocation events were movements.Bychangingthetimelagintheanalysistomaximize
observed, as illustrated in Figure 5a. During these events, the the magnitude of the correlation coefficients, we were able to
POPSlipidthatwasinitiallyboundinthebindingpocketlocated uncoverthesequencesofthesethreemovements.Theresultsin
in the exoplasmic leaflet was successfully flipped to the FigureS7brevealedthattheclosingofthelipid-bindingpocket
cytoplasmicleaflet.In13outofthe50simulations,thebound consistentlyprecededboththemovementoftheA−Pdomains
lipidfailedtocompletetheflippingprocessanddiffusedintothe and the lipid-flipping process. This indicates that an allosteric
exoplasmicleafletofthemembrane(FigureS6a).Theremaining effect may drive the pocket close before the A−P domain
14simulationswereincomplete,inwhichthelipidwastrapped changes its conformation, which is followed by a lipid flip.
inthebindingpocketofATP8A1(FigureS6b).Extendingthe However,itisalsopossiblethattheeventsequenceisanartifact
simulationsforanadditional1000nsresultedinmoreflipping of the switching protocol, which may lead to the minor
events being observed (six repeats completed and two failed), conformational changes to occur first. Therefore, further
indicating that the lipid trapping state is metastable and a investigationsarewarrantedtovalidatethisinfuturestudies.
majorityoftheboundPOPStendtoflipduringtheE2Pi-PL-to- ThelipidheaddensitymapsoftheboundPOPSwereusedto
E1transition(FigureS6b).Therelationshipbetweenthelipid revealthelipid-bindingsitesduringthetranslocationprocess.In
flipping process and the main conformational transitions of theE2Pi-PLandE1states,twobindingsiteswereidentifiedand
ATPA81-CDC50a was analyzed using the time-dependent areshowninFigure5b,c.Lipid-bindingsite1waslocatedinthe
|     |     |     |     |     |     |     | 2622 |     |     |     |     | https://doi.org/10.1021/acs.jctc.3c01222 |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | ---- | --- | --- | --- | --- | ---------------------------------------- | --- | --- | --- |
J.Chem.TheoryComput.2024,20,2618−2629

JournalofChemicalTheoryandComputation pubs.acs.org/JCTC Article
Figure6.LipidtranslocationprocessofATP8A1-CDC50a.(a−c)Zoom-inviewsofthelipidtranslocationprocessofATP8A1-CDC50awiththe
boundlipidinlipid-bindingsite1(a),lipid-bindingsite2(b),andcytoplasmicleafletoftheplasmamembrane(c),respectively.Theproteinisshown
asaribbonwithATP8A1coloredtanandCDC50acoloredlightgray.ThePOPSlipidisshownastheball-and-stickmodelwiththetailcolored
mediumorchidandthelipidheadgroupcoloredorangeandred.Theessentialpolarresiduesinlipid-bindingsite1and2arecoloredlightgreenand
plum,respectively,withthesidechainsshownasastick.
| same binding | pocket     | as    | found    | by the | cryo-EM  | density | maps, |     |     |     |     |     |     |     |
| ------------ | ---------- | ----- | -------- | ------ | -------- | ------- | ----- | --- | --- | --- | --- | --- | --- | --- |
| which was    | surrounded | by    | residues | T100,  | T101,    | P104,   | N352, |     |     |     |     |     |     |     |
| N353, I357,  | I878,      | G879, | L880,    | Y881,  | and N882 | (Figure | 5d).  |     |     |     |     |     |     |     |
Lipid-bindingsite2wasformedbyresiduesF107,V111,S358,
V361,T362,N882,V883,A887,andL891,whichwasidentified
| in our simulations |       | (Figure   | 5e). | The density |       | maps        | of the two |     |     |     |     |     |     |     |
| ------------------ | ----- | --------- | ---- | ----------- | ----- | ----------- | ---------- | --- | --- | --- | --- | --- | --- | --- |
| lipid-binding      | sites | indicated | that | the         | bound | lipid could | move       |     |     |     |     |     |     |     |
betweenthetwobindingsitesintheE2Pi-PLstate,whileitwas
| mainly bound | to  | lipid-binding |     | site 1 | (Figure | 5b). | When we |     |     |     |     |     |     |     |
| ------------ | --- | ------------- | --- | ------ | ------- | ---- | ------- | --- | --- | --- | --- | --- | --- | --- |
switchedofftheE2Pi-PLstateandswitchedontheE1topology,
thelipidinlipid-bindingsite1wassqueezedandtransportedto
lipid-bindingsite2(MovieS1).Then,thetailoftheboundlipid
| changed    | its direction | from    | perpendicular |         | to             | parallel        | to the   |     |     |     |     |     |     |     |
| ---------- | ------------- | ------- | ------------- | ------- | -------------- | --------------- | -------- | --- | --- | --- | --- | --- | --- | --- |
| membrane   | surface       | (Figure | 6a,b).        | With    | the simulation |                 | going, a |     |     |     |     |     |     |     |
| majority   | of the        | bound   | lipids were   | flipped | to             | the cytoplasmic |          |     |     |     |     |     |     |     |
| leaflet of | the membrane  |         | (Figure       | 6c),    | although       | some            | of them  |     |     |     |     |     |     |     |
failedtoflipanddiffusedintotheexoplasmicleaflet.
AsshowninFigure5d,lipid-bindingsite1issurroundedby
the polar residues including T100, T101, N352, N353, Y881, Figure7.LipidtranslocationmechanismoftheP4-ATPaseflippases.
andN882,whichcanselectivelybindtocertaintypesoflipids TheschematicmodelofthelipidtranslocationcyclefortheP4-ATPase
(PSforATP8A1),52whilelipid-bindingsite2playsaroleasthe flippases.Themodelisdepictedwiththesamecolorcodes,asshownin
Figure4.TheE2Pi-PL-to-E1conformationaltransitionconductedhere
intermediateharborthatisimportantforthetranslocationofthe
|     |     |     |     |     |     |     |     | is enclosed | by the | black | dashed box. | The | other | conformational |
| --- | --- | --- | --- | --- | --- | --- | --- | ----------- | ------ | ----- | ----------- | --- | ----- | -------------- |
boundlipid.Interestingly,thedensityblobsatthesamelocation
transitionsthatwerenotsimulatedaredepictedastransparent.Atthe
oflipid-bindingsite2werereportedinthecryo-EMstructures
beginningofthelipidtranslocationprocess,lipid-bindingsite1ofthe
| from different |     | types of | P4-ATPases.55 |     | Additionally, |     | lipid- |     |     |     |     |     |     |     |
| -------------- | --- | -------- | ------------- | --- | ------------- | --- | ------ | --- | --- | --- | --- | --- | --- | --- |
P4-ATPaseflippaseintheE2Pi-PLstatespecificallyattractsandbindsa
binding site 2 is composed of some polar residues, including phospholipid. Subsequently, with the phosphate release at the P
S358, T362, and N882 (Figure 5e). Mutations of these three domain of the P4-ATPase, lipid-binding site 1 undergoes closure,
residuesinthehomologyproteinswerereportedtosignificantly resultinginthedisplacementoftheboundlipidtowardlipid-binding
decrease the transportation ability. The S365A and T369A site 2. Then, the phospholipid leaves lipid-binding site 2 and
mutationsofATP8A2(S358andT362ofATP8A1)displayed translocates toward the inner leaflet of the membrane with the
activity.56 assistance of thermal fluctuations, and the flippase adopts the E1
| significant | reductions           | in  | the ATPase |        |     | The          | N1226A |               |       |     |          |         |                 |     |
| ----------- | -------------------- | --- | ---------- | ------ | --- | ------------ | ------ | ------------- | ----- | --- | -------- | ------- | --------------- | --- |
|             |                      |     |            |        |     |              |        | conformation, | ready | to  | initiate | another | phosphorylation | and |
| mutationof  | Dnf1(correspondingto |     |            | N882of |     | ATP8A1)could |        |               |       |     |          |         |                 |     |
dephosphorylationcycle.
| completely | halt    | the transportation |           | of  | lipids     | even        | though the |              |         |          |          |       |        |          |
| ---------- | ------- | ------------------ | --------- | --- | ---------- | ----------- | ---------- | ------------ | ------- | -------- | -------- | ----- | ------ | -------- |
| mutant     | protein | was still          | localized | on  | the plasma | membrane.53 |            |              |         |          |          |       |        |          |
|            |         |                    |           |     |            |             |            | limitations: | (1) the | implicit | solvent, | which | cannot | properly |
Moreimportantly,theS403YmutationinATP8B1(equivalent
|     |     |     |     |     |     |     |     | reveal the | interaction | between | proteins |     | and water | or charged |
| --- | --- | --- | --- | --- | --- | --- | --- | ---------- | ----------- | ------- | -------- | --- | --------- | ---------- |
toS358ofATP8A1)wasfoundinthepatientswithprogressive
(PFIC1).57 ions; (2) the implicit membrane environment, which cannot
| familial     | intrahepatic | cholestasis |     | type | 1                  |     | These  |           |             |     |                |     |          |               |
| ------------ | ------------ | ----------- | --- | ---- | ------------------ | --- | ------ | --------- | ----------- | --- | -------------- | --- | -------- | ------------- |
|              |              |             |     |      |                    |     |        | show the  | association | and | disassociation |     | of       | lipids around |
| experimental | results      | support     | the | idea | that lipid-binding |     | site 2 |           |             |     |                |     |          |               |
|              |              |             |     |      |                    |     |        | proteins. | The Martini |     | model utilizes |     | explicit | solvent and   |
playsanessentialroleinthelipidtranslocationprocess.Allthese
|     |     |     |     |     |     |     |     | develops | a great | diversity | of lipids, | providing |     | an important |
| --- | --- | --- | --- | --- | --- | --- | --- | -------- | ------- | --------- | ---------- | --------- | --- | ------------ |
findingsdemonstratethatourswitchingGo̅-Martinisimulations
|             |          |     |               |     |                |     |       | computational | tool | for | the understanding |     | of  | interactions |
| ----------- | -------- | --- | ------------- | --- | -------------- | --- | ----- | ------------- | ---- | --- | ----------------- | --- | --- | ------------ |
| effectively | captured | the | E2Pi-PL-to-E1 |     | conformational |     | tran- |               |      |     |                   |     |     |              |
betweenproteinsandlipids,andhasthereforebeenextensively
sition of ATP8A1-CDC50a and shed new light on the lipid studies.24,25,58,59
|     |     |     |     |     |     |     |     | utilized | in this kind | of  |     |     | However, | the elastic |
| --- | --- | --- | --- | --- | --- | --- | --- | -------- | ------------ | --- | --- | --- | -------- | ----------- |
translocationmechanismoftheP4-ATPaseflippase(Figure7).
networkrestraintsinthepreviousMartiniproteinmodelsused
|     |     |     |     |     |     |     |     | to stabilize | the | second | or higher | structures |     | impede the |
| --- | --- | --- | --- | --- | --- | --- | --- | ------------ | --- | ------ | --------- | ---------- | --- | ---------- |
3. DISCUSSION
|     |     |     |     |     |     |     |     | conformational | changes | of  | the proteins. |     | Recently, | the Go̅-like |
| --- | --- | --- | --- | --- | --- | --- | --- | -------------- | ------- | --- | ------------- | --- | --------- | ------------ |
TraditionalGo̅-likeCGmodelshaveobtainedgreatsuccessin Martinimodelwasdevelopedwithcontactmap-basedLennard-
the simulation of protein conformational transition. However, Jones potential replacing the harmonic potential in the elastic
thedevelopmentofthesemodelshasbeenimpededbyseveral network,whichshowedsimilardynamicsofproteinscompared
|     |     |     |     |     |     |     | 2623 |     |     |     |     | https://doi.org/10.1021/acs.jctc.3c01222 |     |     |
| --- | --- | --- | --- | --- | --- | --- | ---- | --- | --- | --- | --- | ---------------------------------------- | --- | --- |
J.Chem.TheoryComput.2024,20,2618−2629

JournalofChemicalTheoryandComputation pubs.acs.org/JCTC Article
to all-atom models.27 This pioneering study simulated the from the E2Pi-PL state to the E1 state. The entire process of
folding process of small proteins and the unfolding process lipid translocation during these conformational changes was
induced by external pulling forces,27 which opened the capturedforthefirsttime,andtheunderlyingmechanismofP4-
possibility of exploring large conformational space by using ATPase-mediated lipid translocation was elucidated. This is a
the Martini force field. The next question is whether one can significant advantage of the switching Go̅-Martini method in
simulate conformational transitions of proteins between two simulatingmembraneproteinscomparedtootherexistingGo̅-
knownstateswiththeMartiniforcefield.Withthereleaseofthe likemethods.However,certainimportantbiologicalmolecules
latest Martini 325 and the inspiration of the study of a small and residues, such as glycans, have not been covered by the
molecular switch recently,29 here we have developed the currentMartini3forcefield.Therefore,somesystemscannotbe
switching Go̅-Martini method by combining the classical simulated properly yet, such as the spike protein, in which N-
switchingapproachwiththeGo̅-likeMartinimodel. glycans play an important role.64−66 Still, we were able to
TheswitchingGo̅-Martinimethodiscapableofsamplingthe reproducetheopen-to-closedtransitionofthespikeproteinin
conformational transition pathways that are qualitatively theabsenceofN-glycans,andtheresultsareinlinewithprevious
consistent with results obtained from previous CG and all- all-atomsimulations(FigureS8).66,67
atom MD simulations. Our validation process encompassed Although the approach has demonstrated success in
three benchmarking systems that had been quantitatively simulatingconformationaltransitionsofproteins,itisimportant
studied by CG and all-atom simulations, including GlnBP, to acknowledge the limitations of our method. First, the
AdK, and β2AR, spanning from simple to frustrated and from switching Go̅-Martini method needs structures of two known
soluble to membrane-embedded. These well-tested systems states of multiple-state proteins to sample the conformational
validatedthatourmethodcancorrectlycapturetheconforma- transitionsbetweenthesestates.Thisisthecommonchallenge
tional changes of proteins without fine-tuning parameters. faced by all the switching-like approaches23 and TMD.60 This
Additionally, compared with the unbiased all-atom MD limitationcanbealleviatedbythefastdevelopmentofCryo-EM
simulations, the Switching Go̅-Martini method can offer a techniques7,68 and deep-learning methods to solve or predict
significantly more efficient and rapid means of sampling multiple-state structures of a protein.69,70 We expect that our
conformational transitions. For instance, when studying the methodcanbeeffectivelycombinedwiththeserapidlyevolving
deactivationprocessofβ2AR,all-atomMDsimulationsrequired techniques to enhance our understanding of the dynamic
approximately 600 μs to observe 39 deactivation events.48 In mechanismsunderlyingtheproteins.
contrast, our approach successfully simulated 40 repeated Second, the default settings for constructing contact map
deactivation processes in a total time of 40 μs. Furthermore, interactions used here may not be optimal for all cases. It is
when the simulation speed on a common workstation is important to note that there is still room for improvement in
considered, the all-atom model typically achieves a rate of constructing contact maps and describing these interactions
around 100 ns per day, while the Martini model exhibits an more accurately. Notably, efforts have been made in this
impressive rate of approximately 6000 ns per day. This means direction by Mahmood et al. and Pedersen et al.,28,71 and
that our method can sample conformational transitions more optimizing the contacts on a case-by-case basis may further
than 900 times faster than the unbiased all-atom model. enhance the performance in correctly sampling the conforma-
Therefore, the switching Go̅-Martini method represents a tional transition pathways of proteins. However, fine-tuning
significant advantage in the sampling efficiency of conforma- parametersforeachindividualcaseisbeyondthescopeofthis
tional transitions compared to unbiased all-atom simulations, workaswehopetoprovideamorestraightforwardandversatile
althoughitisonlyqualitative. protocol that can quickly provide possible transition paths
The switching Go̅-Martini method resembles the “targeted withoutextensiveparameteradjustmentsatthisstage.
molecular dynamics” (TMD) simulations,60 in the sense that Third, our method cannot guarantee that the captured
theycanbothefficientlysimulatetheconformationaltransition pathwaysofconformationaltransitionsareallreasonable.Thisis
betweentwostates.However,whenTMDisadopted,onlyone duetothefactthattheso-called“verticalexcitation”ofproteins
transition pathway can be obtained, which may significantly when switching the state may lead to proteins falling into the
deviate from the most probable pathway, so some of the final state through an inappropriate pathway. This intrinsic
following methods have to be utilized to refine the transition problem pertains to all the Go̅-like models employing the
pathway. In contrast, the switching Go̅-Martini method can switchingapproach23andarisesfromtheoverestimatedenergy
provide multiple, more physical pathways, a significant duringtheswitchingprocessforovercomingthetransitionstates
advantage over TMD. Also, these transition pathways can be (Figure 1a).23 For example, in the AdK simulations, 21.4% of
used by follow-up methods, such as resolution transforma- oursimulationsutilizedthemiddlepathwayinwhichNMPand
tion61,62 and string method,63 for the exploration of the most LID domains opened concurrently (Figure S2f). This specific
probable transition pathway and quantitative free-energy phenomenon had not been previously reported in other CG
calculations. Considering the wide usage of TMD, we expect simulationsemployingmultiple-basinmethods,21,22whereonly
thatswitchingGo̅-Martinicanprovideahighlyusefulapproach the NMP-closing pathway and LID-closing pathway were
forall-atomandquantitativefree-energycalculations. observed. The discrepancy could potentially be attributed to
The switching Go̅-Martini method is well-suited for the switching approach in our simulations, allowing proteins
investigating protein−lipid interactions during protein con- with higher energy levels to adopt improper pathways.
formational transitions. By utilizing the explicit-membrane Additionally,themethodcannotquantitativelydepictthefree-
modelsintheMartiniforcefield,wewereabletosimulatethe energy landscape and the corresponding kinetics between the
lipid−protein interactions in the lipid translocation process of two states. This limitation arises from the fact that such
the P4-ATPases. A series of 50 independent simulations informationreliesontheresidencetimeofthesimulatedprotein
employingtheswitchingGo̅-Martinimethodrevealedexquisite stayinginastate,whichismanuallycontrolledbytheswitching
details of the conformational transitions of ATP8A1-CDC50a method. Despite these limitations, the results from our
2624 https://doi.org/10.1021/acs.jctc.3c01222
J.Chem.TheoryComput.2024,20,2618−2629

JournalofChemicalTheoryandComputation pubs.acs.org/JCTC Article
benchmarking systems showcased that our switching Go̅- vermouth-martinize). Additional Lennard-Jones interactions
Martini method can often sample the correct conformational for the Go̅-like model were generated based on the OV and
transition pathways for multiple-state proteins, which can be rCSU contacts (http://info.ifpan.edu.pl/~rcsu/rcsu/index.
usedforfurtherpathoptimization,followedbyquantitativefree- html) and set up using theprogram create_goVirt.py (http://
energycalculations,similartothewidelyusedTMDsimulations. md.chem.rug.nl) with a distance cutoff of 3−11 Å and a
Finally, although surrounding molecules such as water can dissociationenergyofε=12.0kJ/mol.TheopenstateofGlnBP
promptly adjust their positions in response to the conforma- was chosen as the initial state in our simulations. The CG
tional transitions of proteins in the switching Go̅-Martini proteinandwaterwereplacedinarectangularbox(80×80×70
simulations,itispossiblethatlargesurroundingmoleculeswith Å3)usingtheprograminsane.py.77150mMNaClwasaddedto
slowmotionsmaystruggletoadapttheirstructurestokeepup keepthewholesystemchargeneutral.50CGsimulationswith
with the conformational changes of the protein during the 300×3nswereperformedtoinvestigatetheopen-closed-open
switchingprocess.Thismaypartiallyexplainwhyonlyaportion conformational transition path of GlnBP. Additionally, to
of the lipid molecules was successfully transported in the further test the robustness of the method, one simulation
simulationsofthelipidflippase. comprising 10 cycles of open ↔closed transitions was also
Therefore, a multiple-basin Go̅-Martini method, combined performedwiththesameparameters.
with path optimization strategies, would be desired to address 4.3.AdenylateKinaseCGModel.Theopen-andclosed-
the above limitations. These are under development, which in stateCGmodelsofAdKwerebuiltusingtheMartini3forcefield
the future can be used to obtain more realistic and accurate and the structures with the PDB codes 4AKE39 and 1ANK,38
transitionsbetweendistinctstatesofproteinsandallowproteins respectively. The topologies of the open- and closed-states of
toundergospontaneouschangesinresponsetothemodulation AdKweregeneratedusingtheprogrammartinize2.py(https://
exertedbythesurroundingsmallmolecules.20−22,72
github.com/marrink-lab/vermouth-martinize).AdditionalLen-
nard-Jones interactions for the Go̅-like model were generated
4. MATERIALSANDMETHODS basedontheOVandrCSUcontacts(http://info.ifpan.edu.pl/
4.1.SimulationSettings.Allsimulationsinourworkwere ~rcsu/rcsu/index.html) and set up using the program
performedusingtheCGforcefieldMartini325(version3.0.0) create_goVirt.py (http://md.chem.rug.nl) with a distance
with the MD package Gromacs73 (version 2020.x or 2021.x). cutoffof3−11Åandadissociationenergyofε=12.0kJ/mol.
Details about generating protein CG models and setting up The closed state of AdK was chosen as the initial state in our
simulationsystemsaregiveninthefollowingsections.Forthe simulations. The CG protein and water were placed in a
MD simulations, the systems were minimized and then rectangular box (70 × 90 × 90 Å3) using the program
equilibrated in the NPT ensemble with positional restraints
insane.py.77150mMNaClwasaddedtokeepthewholesystem
(10kJ/mol/Å2)ontheBBsofCGproteins.Productionswere charge neutral. 70 CG simulations with 100 × 2 ns were
conductedataconstantisotropicorsemi-isotropicpressureof1 performed to investigate the closed-to-open conformational
atm and a temperature of 310.15 K according to the systems. transitionpathofAdK.
The V-rescale algorithm74 with a coupling time of 1.0 ps was 4.4.β 2 -AdrenergicReceptorCGModel.Theactive-and
used to maintain the temperature of the systems and the inactive-stateCGmodelsofβ2ARwerebuiltusingtheMartini3
Parrinello-Rahmanthermostat75withacouplingtimeof12.0ps force field and the structures with the PDB codes 3SN646
was performed to maintain the pressure of the systems. The and2RH147 respectively. The missing loop and mutations
electrostaticinteractionandthevanderWaalsinteractionwere (residues176−178,mutationsM96TandM98T)of3SN6were
bothcutoffat11Åandthelong-rangeelectrostaticinteraction
repairedusingModeller.78Thesequencesofbothproteinswere
was computed by using the reaction-field method76 with a trimmedtothesamelength(residues30−230and265−341).
relativedielectricconstant(epsilon_r=15). The topologies of the active and inactive states of β2AR were
The switching method for conformational transitions of generated using the program martinize2.py (https://github.
different states of proteins is introduced here. Briefly, the com/marrink-lab/vermouth-martinize). Additional Lennard-
systemswerefirstsimulatedtooscillatearoundStateAbyusing JonesinteractionsfortheGo̅-likemodelweregeneratedbased
thetopologyofStateA.BeforecompletelyswitchingtoStateB, ontheOVandrCSUcontacts(http://info.ifpan.edu.pl/~rcsu/
the systems must be relaxed to fit the new topology by rcsu/index.html)andsetupusingtheprogramcreate_goVirt.py
performingashortandslowsimulation(1000steps×0.002ps (http://md.chem.rug.nl)withadistancecutoffof3−11Åanda
per step) using the topology of State B. Then, production dissociationenergyofε=12.0kJ/mol.Theactivestateofβ2AR
simulations were conducted using the topology of State B, was chosen as the initial state in our simulations. The CG
duringwhichthesystemscouldbegraduallytransitedtoStateB. proteinwasembeddedintoaPOPCbilayerwithinarectangular
AllsimulationparametersforrunningCGsystemsarelistedin box(80×80×100Å3)usingtheprograminsane.py.77150mM
Table S1, and the results of transition pathways are shown in NaClwasaddedtokeepthewholesystemchargeneutral.40CG
TableS2.IntheSupportingInformation,weprovideatutorialto simulationswith500×2nswereperformedtoinvestigatethe
showhowtosetupsuchsimulations,usingtheactive-to-inactive active-to-inactiveconformationaltransitionpathofβ2AR.
transitionofβ2ARasanexample. 4.5. P4-ATPase Flippase ATP8A1-CDC50a CG Model.
4.2. Glutamine-Binding Protein CG Model. The open- TheCGmodelsoftheE2Pi-PLandE1statesoftheP4ATPase
and closed-state CG models of glutamine-binding protein ATP8A1-CDC50acomplexwerebuiltusingtheMartini3force
(GlnBP) were built using the Martini 3 force field and the fieldandthestructureswiththePDBcodes6K7Mand6K7G,
structures with the PDB codes 1GGG34 and 1WDN,33 respectively.52Themissingloops(residues237−242and434−
respectively. The sequences of both proteins were trimmed to 445)ofATP8A1wererepairedusingModeller.78Thesequences
havethesamelength(residues5−224).Thetopologiesofthe of both structures were trimmed to have the same lengths
open- and closed-states of GlnBP were generated using the (residues35−696and725−1063ofATP8A1andresidues27−
program martinize2.py (https://github.com/marrink-lab/ 350ofCDC50a).ThetopologiesoftheE2Pi-PLandE1statesof
2625 https://doi.org/10.1021/acs.jctc.3c01222
J.Chem.TheoryComput.2024,20,2618−2629

JournalofChemicalTheoryandComputation pubs.acs.org/JCTC Article
ATP8A1-CDC50a were generated using the program martini- distancebetweenthetwohelices(residues100−104and878−
ze2.py (https://github.com/marrink-lab/vermouth-martinize). 883) constructing the window of the lipid-binding pocket.
Additional Lennard-Jones interactions for the Go̅-like model ATP8A1-CDC50a transitions were classified as the main
A−P
were generated based on the OV and rCSU contacts (http:// pathway if the distance of domains of transition states
info.ifpan.edu.pl/~rcsu/rcsu/index.html), which were set up waslessthan34Åandthewidthofthepocketwaslessthan11Å
using the program create_goVirt_for_multimer.py modified orthemiddlepathwayifthedisassociationofA−Pdomainsand
basedontheinitialprogramcreate_goVirt.py(http://md.chem. the closure of the lipid-binding pocket happened simulta-
|            |            |      |            |     |           | 3−11 |         | neously. The | representative | intermediate |     | structures | were |
| ---------- | ---------- | ---- | ---------- | --- | --------- | ---- | ------- | ------------ | -------------- | ------------ | --- | ---------- | ---- |
| rug.nl) by | ourselves, | with | a distance |     | cutoff of |      | Å and a |              |                |              |     |            |      |
dissociation energy of ε = 12.0 kJ/mol. The E2Pi-PL state of obtainedbyusingthek-meansclusteringmethod.
ATP8A1-CDC50a was chosen as the initial state in our 4.9. Simulation Analysis. The lipid head density was
simulations. The binding PS lipid found in the cryo-EM obtainedbycomputingtheoccupancyofthelipidheadsofthe
structure was also retained and converted to the POPS CG boundPOPSinthethree-dimensionalspaceusingtheVolmap
pluginofVMD.79Thegridpointshadaspacingdistanceof1Å.
model,whilethephosphateligandwasconsideredimplicitand
notdisplayedinoursimulations.TheCGproteinandthebound The polar residues around the binding sites were obtained by
lipid were embedded into an asymmetric membrane within a analyzing the interaction between the bound lipid heads and
rectangular box (120 × 120 × 190 Å3) using the program residueswithadistancecutoffof6Åandanoccupancycutoffof
insane.py,77 in which POPS occupied 10% of the cytoplasmic 40%. Additionally, geometry calculation, rmsd, and protein−
|     |     |     |     |     |     |     |     | lipid interaction | were analyzed | with | MDAnalysis.80 | The | time- |
| --- | --- | --- | --- | --- | --- | --- | --- | ----------------- | ------------- | ---- | ------------- | --- | ----- |
leafletwithPOPCoccupyingtheremainingmembrane.150mM
NaClwasaddedtokeepthewholesystemchargeneutral.50CG dependent Pearson correlation coefficient was employed to
simulations of 200 ns (E2Pi-PL) plus 800 ns (E1) were evaluate the synchronicity of the movements of ATP8A1-
performed to investigate the E2Pi-PL → E1 conformational CDC50a during the lipid-flipping process. The time lags that
transition path and the lipid translocation process of the P4- maximized the magnitude of the correlation coefficients were
|                      |     |     |          |     |           |          |     | used to uncover | the sequences |     | of these | movements. | All |
| -------------------- | --- | --- | -------- | --- | --------- | -------- | --- | --------------- | ------------- | --- | -------- | ---------- | --- |
| ATPase ATP8A1-CDC50a |     |     | complex. |     | For those | in which | the |                 |               |     |          |            |     |
lipid was trapped in the binding pocket of ATP8A1, an structural figures and the movie were generated using
ChimeraX.81
additional1000nswasconductedtoinvestigatethestabilityof
| thelipid-trappingstate. |     |     |     |     |     |     |     | ■   |     |     |     |     |     |
| ----------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
4.6. Classification of AdK Conformational Transition ASSOCIATEDCONTENT
Pathways. Conformational transition paths of AdK were DataAvailabilityStatement
classified as the LID-closing pathway, NMP-closing pathway, The input, code, and tutorial for the switching Go̅-Martini
| and middle | pathway | by  | using | the combination |     | of two | angles |     |     |     |     |     |     |
| ---------- | ------- | --- | ----- | --------------- | --- | ------ | ------ | --- | --- | --- | --- | --- | --- |
simulationsareprovidedintheSupportingInformation,aswell
| θ andθ | .Theanglesweredefinedaccordingtothecenter |     |     |     |     |     |     |              |                                    |     |     |     |     |
| ------ | ----------------------------------------- | --- | --- | --- | --- | --- | --- | ------------ | ---------------------------------- | --- | --- | --- | --- |
| NMP    | LID                                       |     |     |     |     |     |     | as on GitHub | (https://github.com/ComputBiophys/ |     |     |     |     |
35−55,
of mass of the following atoms: BB atoms of residues SwitchingGo-Martini).
| 90−100,and115−125forθ |     |         |     | andBBatomsofresidues125− |                   |     |      | *                        |     |     |     |     |     |
| --------------------- | --- | ------- | --- | ------------------------ | ----------------- | --- | ---- | ------------------------ | --- | --- | --- | --- | --- |
|                       |     |         | NMP |                          |                   |     |      | sı SupportingInformation |     |     |     |     |     |
| 153, 115−125,         | and | 204−212 |     | for θ                    | . AdK transitions |     | were |                          |     |     |     |     |     |
LID The Supporting Information is available free of charge at
| classifiedasLID-closingpathwaysifθ |     |     |                                   |     | oftransitionstateswas |     |     |                                                    |     |     |     |     |     |
| ---------------------------------- | --- | --- | --------------------------------- | --- | --------------------- | --- | --- | -------------------------------------------------- | --- | --- | --- | --- | --- |
|                                    |     |     |                                   | NMP |                       |     |     | https://pubs.acs.org/doi/10.1021/acs.jctc.3c01222. |     |     |     |     |     |
| morethan70°andθ                    |     |     | waslessthan90°,NMP-closingpathway |     |                       |     |     |                                                    |     |     |     |     |     |
LID
ifθ oftransitionstateswaslessthan50°andθ Simulation parameters and transition pathway summary
| NMP |     |     |     |     |     | LID wasmore |     |     |                    |                   |     |             |     |
| --- | --- | --- | --- | --- | --- | ----------- | --- | --- | ------------------ | ----------------- | --- | ----------- | --- |
|     |     |     |     |     |     |             |     | and | additional details | of conformational |     | transitions | of  |
than105°,ormiddlepathwayforthosenotbelongtotheLID/
GlnBP,AdK,β2AR,ATP8A1-CDC50a,andSARS-CoV-
| NMP-closing | pathway. |     | The representative |     | intermediate |     | struc- |     |     |     |     |     |     |
| ----------- | -------- | --- | ------------------ | --- | ------------ | --- | ------ | --- | --- | --- | --- | --- | --- |
tureswereobtainedbyusingthek-meansclusteringmethod. 2spikeproteins(PDF)
4.7.Classificationofβ2ARConformationalTransition
LipidtranslocationprocessofATP8A1-CDC50a(MP4)
Pathways.Conformationaltransitionpathsofβ2ARdeactiva-
|     |     |     |     |     |     |     |     | Tutorial | for setting | up  | the switching | Go̅-Martini |     |
| --- | --- | --- | --- | --- | --- | --- | --- | -------- | ----------- | --- | ------------- | ----------- | --- |
tion were classified as the normal pathway and abnormal simulations(ZIP)
pathwaybyusingthecombinationofhelix6tohelix3distance
| andthermsdoftheNPxxYmotif(residues322−327)alignedto |     |     |     |     |     |     |     | ■   |     |     |     |     |     |
| --------------------------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
AUTHORINFORMATION
theinactivestate.Helix6−helix3distancewasmeasuredasthe
CorrespondingAuthor
| distance between |     | R131 | and L272 | BB  | atoms. β2AR | transitions |     |     |     |     |     |     |     |
| ---------------- | --- | ---- | -------- | --- | ----------- | ----------- | --- | --- | --- | --- | --- | --- | --- |
wereclassifiedasnormalpathwayifthehelix6−helix3distance ChenSong−Peking-TsinghuaCenterforLifeSciences,
oftransitionstateswasmorethan12ÅandthermsdofNPxxY AcademyforAdvancedInterdisciplinaryStudies,Peking
motifwaslessthan0.6Åorabnormalpathwayifthehelix6− University,Beijing100871,China;CenterforQuantitative
Biology,AcademyforAdvancedInterdisciplinaryStudies,
helix3distanceoftransitionstateswaslessthan12Åandthe
rmsdofNPxxYmotifwasmorethan0.6Å.Therepresentative PekingUniversity,Beijing100871,China; orcid.org/0000-
intermediate structures were obtained by using the k-means 0001-9730-3216;Email:c.song@pku.edu.cn
clusteringmethod.
Author
4.8.ClassificationofATP8A1-CDC50aConformational
Transition Pathways. SongYang−Peking-TsinghuaCenterforLifeSciences,Academy
|     |     |     | Conformational |     | transition | paths | of  |     |     |     |     |     |     |
| --- | --- | --- | -------------- | --- | ---------- | ----- | --- | --- | --- | --- | --- | --- | --- |
forAdvancedInterdisciplinaryStudies,PekingUniversity,
| ATP8A1-CDC50a |     | were | classified | as  | the main | pathway | and |     |     |     |     |     |     |
| ------------- | --- | ---- | ---------- | --- | -------- | ------- | --- | --- | --- | --- | --- | --- | --- |
Beijing100871,China;CenterforQuantitativeBiology,
middlepathwaybyusingacombinationofthedistanceofA−P
AcademyforAdvancedInterdisciplinaryStudies,Peking
domainsandthewidthofthelipid-bindingpocket.Thedistance
oftheA−Pdomainswasmeasuredasthedistancebetweenthe University,Beijing100871,China; orcid.org/0000-0001-
|           |        |         |     |             |           |     | 35−51 | 9712-8702 |     |     |     |     |     |
| --------- | ------ | ------- | --- | ----------- | --------- | --- | ----- | --------- | --- | --- | --- | --- | --- |
| center of | massof | BBatoms | of  | the Adomain | (residues |     |       |           |     |     |     |     |     |
and134−279)andthePdomain(residues384−416and649− Completecontactinformationisavailableat:
819).Thewidthofthelipid-bindingpocketwascalculatedasthe https://pubs.acs.org/10.1021/acs.jctc.3c01222
|     |     |     |     |     |     |     | 2626 |     |     |     | https://doi.org/10.1021/acs.jctc.3c01222 |     |     |
| --- | --- | --- | --- | --- | --- | --- | ---- | --- | --- | --- | ---------------------------------------- | --- | --- |
J.Chem.TheoryComput.2024,20,2618−2629

JournalofChemicalTheoryandComputation pubs.acs.org/JCTC Article
AuthorContributions tional motions of proteins: Structure-based molecular dynamics
S.Y.andC.S.conceivedtheideaanddesignedtheresearch.S.Y. simulations.Proc.Natl.Acad.Sci.U.S.A.2006,103,11844−11849.
conducted simulations and analyzed data. S.Y. and C.S. wrote (21) Lu, Q.; Wang, J. Single molecule conformational dynamics of
|     |     |     |     |     |     |     | adenylate | kinase: | Energy | landscape, | structural | correlations, |     | and |
| --- | --- | --- | --- | --- | --- | --- | --------- | ------- | ------ | ---------- | ---------- | ------------- | --- | --- |
themanuscript.C.S.acquiredfundingandsupervisedthework.
transitionstateensembles.J.Am.Chem.Soc.2008,130,4772−4783.
Notes
|     |     |     |     |     |     |     | (22) Shinobu, | A.; | Kobayashi, | C.; | Matsunaga, | Y.; Sugita, | Y.  | Coarse- |
| --- | --- | --- | --- | --- | --- | --- | ------------- | --- | ---------- | --- | ---------- | ----------- | --- | ------- |
Theauthorsdeclarenocompetingfinancialinterest. GrainedModelingofMultiplePathwaysinConformationalTransitions
| ■   |     |     |     |     |     |     | ofMulti-DomainProteins.J.Chem.Inf.Model.2021,61,2427−2443. |     |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | ---------------------------------------------------------- | --- | --- | --- | --- | --- | --- | --- |
ACKNOWLEDGMENTS (23)Koga,N.;Takada,S.Folding-basedmolecularsimulationsreveal
mechanismsoftherotarymotorF1-ATPase.Proc.Natl.Acad.Sci.U.S.A.
WethankDr.YujiSugitaandDr.ChigusaKobayashiatRIKEN
2006,103,5367−5372.
| for insightful | suggestions | provided | through | numerous |     | dis- |     |     |     |     |     |     |     |     |
| -------------- | ----------- | -------- | ------- | -------- | --- | ---- | --- | --- | --- | --- | --- | --- | --- | --- |
(24)Marrink,S.J.;Risselada,H.J.;Yefimov,S.;Tieleman,D.P.;de
| cussions, | and we thank | Dr. Long | Li at Peking |     | University | for |              |     |         |       |        |                |       |     |
| --------- | ------------ | -------- | ------------ | --- | ---------- | --- | ------------ | --- | ------- | ----- | ------ | -------------- | ----- | --- |
|           |              |          |              |     |            |     | Vries, A. H. | The | MARTINI | force | field: | Coarse grained | model | for |
criticalreadingofthemanuscript.Thisworkwassupportedby biomolecularsimulations.J.Phys.Chem.B2007,111,7812−7824.
theNationalKeyR&DProgramofChina(2021YFE0108100). (25)Souza,P.C.;Alessandri,R.;Barnoud,J.;Thallmair,S.;Faustino,
■ I.; Grünewald, F.; Patmanidis, I.; Abdizadeh, H.; Bruininks, B. M.;
REFERENCES Wassenaar,T.A.;Kroon,P.C.;Melcr,J.;Nieto,V.;Corradi,V.;Khan,
|          |                  |             |             |     |              |     | H.M.;Domanś | ki,J.;Javanainen,M.;Martinez-Seara,H.;Reuter,N.; |     |     |     |     |     |     |
| -------- | ---------------- | ----------- | ----------- | --- | ------------ | --- | ------------ | ------------------------------------------------ | --- | --- | --- | --- | --- | --- |
| (1) Tam, | R.; Saier, M. H. | Structural, | functional, | and | evolutionary |     |              |                                                  |     |     |     |     |     |     |
Best,R.B.;Vattulainen,I.;Monticelli,L.;Periole,X.;Tieleman,D.P.;
relationshipsamongextracellularsolute-bindingreceptorsofbacteria.
deVries,A.H.;Marrink,S.J.Martini3:ageneralpurposeforcefieldfor
Microbiol.Rev.1993,57,320−346.
coarse-grainedmoleculardynamics.Nat.Methods2021,18,382−388.
| (2) Dzeja, | P.; Terzic, A. | Adenylate | kinase | and | AMP signaling |     |     |     |     |     |     |     |     |     |
| ---------- | -------------- | --------- | ------ | --- | ------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
(26)Negami,T.;Shimizu,K.;Terada,T.Coarse-grainedmolecular
| networks: | metabolic monitoring, |     | signal communication |     | and | body |                     |     |            |                |     |        |         |     |
| --------- | --------------------- | --- | -------------------- | --- | --- | ---- | ------------------- | --- | ---------- | -------------- | --- | ------ | ------- | --- |
|           |                       |     |                      |     |     |      | dynamics simulation |     | of protein | conformational |     | change | coupled | to  |
energysensing.Int.J.Mol.Sci.2009,10,1729−1772.
ligandbinding.Chem.Phys.Lett.2020,742,137144.
| (3) Kefauver, | J. M.; Ward, | A. B.; | Patapoutian, | A.  | Discoveries | in  |            |        |          |                  |     |       |           |     |
| ------------- | ------------ | ------ | ------------ | --- | ----------- | --- | ---------- | ------ | -------- | ---------------- | --- | ----- | --------- | --- |
|               |              |        |              |     |             |     | (27) Poma, | A. B.; | Cieplak, | M.; Theodorakis, |     | P. E. | Combining | the |
structureandphysiologyofmechanicallyactivatedionchannels.Nature
|     |     |     |     |     |     |     | MARTINI | and Structure-Based |     | Coarse-Grained |     | Approaches |     | for the |
| --- | --- | --- | --- | --- | --- | --- | ------- | ------------------- | --- | -------------- | --- | ---------- | --- | ------- |
2020,587,567−576.
|                |                  |     |                 |     |            |       | Molecular | Dynamics | Studies | of  | Conformational |     | Transitions | in  |
| -------------- | ---------------- | --- | --------------- | --- | ---------- | ----- | --------- | -------- | ------- | --- | -------------- | --- | ----------- | --- |
| (4) Philipson, | L. H. β-Agonists |     | and metabolism. |     | J. Allergy | Clin. |           |          |         |     |                |     |             |     |
Proteins.J.Chem.TheoryComput.2017,13,1366−1374.
Immunol.2002,110,S313−S317.
|                 |            |            |     |            |            |     | (28) Mahmood, |                | M. I.; Poma, | A.    | B.; Okazaki, | K. i. Optimizing |     | Go̅-  |
| --------------- | ---------- | ---------- | --- | ---------- | ---------- | --- | ------------- | -------------- | ------------ | ----- | ------------ | ---------------- | --- | ----- |
| (5) Wickstrand, | C.; Nogly, | P.; Nango, | E.; | Iwata, S.; | Standfuss, | J.; |               |                |              |       |              |                  |     |       |
|                 |            |            |     |            |            |     | MARTINI       | coarse-grained |              | model | for F-BAR    | protein          | on  | Lipid |
Neutze,R.Bacteriorhodopsin:Structuralinsightsrevealedusingx-ray
lasersandsynchrotronradiation.Annu.Rev.Biochem.2019,88,59−83. membrane.Front.Mol.Biosci.2021,8,619381.
(6)Stiller,J.B.;Otten,R.;Häussinger,D.;Rieder,P.S.;Theobald,D. (29)Vainikka,P.;Marrink,S.J.Martini3Coarse-GrainedModelfor
L.;Kern,D.Structuredeterminationofhigh-energystatesinadynamic Second-GenerationUnidirectionalMolecularMotorsandSwitches.J.
Chem.TheoryComput.2023,19,596−604.
proteinensemble.Nature2022,603,528−535.
(7)Zhang,S.;Zou,S.;Yin,D.;Zhao,L.;Finley,D.;Wu,Z.;Mao,Y. (30)Hyeon,C.;Lorimer,G.H.;Thirumalai,D.Dynamicsofallosteric
transitionsinGroEL.Proc.Natl.Acad.Sci.U.S.A.2006,103,18939−
USP14-regulatedallosteryofthehumanproteasomebytime-resolved
| cryo-EM.Nature2022,605,567−574. |     |     |     |     |     |     | 18944. |     |     |     |     |     |     |     |
| ------------------------------- | --- | --- | --- | --- | --- | --- | ------ | --- | --- | --- | --- | --- | --- | --- |
(8)Hoffer,N.Q.;Woodside,M.T.Probingmicroscopicconforma- (31)Yao,X.Q.;Kenzaki,H.;Murakami,S.;Takada,S.Drugexport
tional dynamics in folding reactions by measuring transition paths. andallostericcouplinginamultidrugtransporterrevealedbymolecular
Curr.Opin.Chem.Biol.2019,53,68−74. simulations.Nat.Commun.2010,1,117−118.
(9) Sugita, Y.; Okamoto, Y. Replica-exchange molecular dynamics (32) Brandani, G. B.; Takada, S. Chromatin remodelers couple
methodforproteinfolding.Chem.Phys.Lett.1999,314,141−151. inchworm motion with twist-defect formation to slide nucleosomal
(10)Laio,A.;Parrinello,M.Escapingfree-energyminima.Proc.Natl. DNA.PLoSComput.Biol.2018,14,No.e1006512.
Acad.Sci.U.S.A.2002,99,12562−12566. (33)Sun,Y.J.;Rose,J.;Wang,B.C.;Hsiao,C.D.Thestructureof
(11)Torrie,G.M.;Valleau,J.P.Nonphysicalsamplingdistributions glutamine-binding protein complexed with glutamine at 1.94 Å
inMonteCarlofree-energyestimation:Umbrellasampling.J.Comput. resolution: Comparisons with other amino acid binding proteins. J.
| Phys.1977,23,187−199. |     |     |     |     |     |     | Mol.Biol.1998,278,219−229. |     |     |     |     |     |     |     |
| --------------------- | --- | --- | --- | --- | --- | --- | -------------------------- | --- | --- | --- | --- | --- | --- | --- |
(12)Husic,B.E.;Pande,V.S.MarkovStateModels:FromanArttoa (34)Hsiao,C.D.;Sun,Y.J.;Rose,J.;Wang,B.C.Thecrystalstructure
Science.J.Am.Chem.Soc.2018,140,2386−2396. ofglutamine-bindingproteinfromEscherichiacoli.J.Mol.Biol.1996,
| (13)Riniker,S.;Allison,J.R.;vanGunsteren,W.F.OnDeveloping |     |     |     |     |     |     | 262,225−242. |     |     |     |     |     |     |     |
| --------------------------------------------------------- | --- | --- | --- | --- | --- | --- | ------------ | --- | --- | --- | --- | --- | --- | --- |
Coarse-GrainedModelsforBiomolecularSimulation:AReview.Phys. (35)Zhang,L.;Wu,S.;Feng,Y.;Wang,D.;Jia,X.;Liu,Z.;Liu,J.;
Chem.Chem.Phys.2012,14,12423−12430. Wang,W.Ligand-boundglutaminebindingproteinassumesmultiple
(14) Noid, W. G. Perspective: Coarse-grained Models for metastablebindingsiteswithdifferentbindingaffinities.Commun.Biol.
| BiomolecularSystems.J.Chem.Phys.2013,139,090901. |     |     |     |     |     |     | 2020,3,419. |     |     |     |     |     |     |     |
| ------------------------------------------------ | --- | --- | --- | --- | --- | --- | ----------- | --- | --- | --- | --- | --- | --- | --- |
(15)Marrink,S.J.;Tieleman,D.P.PerspectiveontheMartiniModel. (36) Kooshapur, H.; Ma, J.; Tjandra, N.; Bermejo, G. A. NMR
Chem.Soc.Rev.2013,42,6801−6822. AnalysisofApoGlutamine-BindingProteinExposesChallengesinthe
(16) Saunders, M. G.; Voth, G. A. Coarse-Graining Methods for Study of Interdomain Dynamics. Angew. Chem. Int. Ed. 2019, 58,
| ComputationalBiology.Annu.Rev.Biophys.2013,42,73−93. |     |     |     |     |     |     | 16899−16902. |     |     |     |     |     |     |     |
| ---------------------------------------------------- | --- | --- | --- | --- | --- | --- | ------------ | --- | --- | --- | --- | --- | --- | --- |
(17)Pak,A.J.;Voth,G.A.AdvancesinCoarse-GrainedModelingof (37)Feng,Y.;Zhang,L.;Wu,S.;Liu,Z.;Gao,X.;Zhang,X.;Liu,M.;
MacromolecularComplexes.Curr.Opin.Struct.Biol.2018,52,119− Liu,J.;Huang,X.;Wang,W.ConformationalDynamicsofapo-GlnBP
126. RevealedbyExperimentalandComputationalAnalysis.Angew.Chem.
(18) Marrink, S. J.; Monticelli, L.; Melo, M. N.; Alessandri, R.; Int.Ed.2016,55,13990−13994.
Tieleman,D.P.;Souza,P.C.T.TwoDecadesofMartini:BetterBeads, (38)Berry,M.B.;Meador,B.;Bilderback,T.;Liang,P.;Glaser,M.;
Broader Scope. WIREs Computational Molecular Science 2023, 13, Phillips,G.N.Theclosedconformationofahighlyflexibleprotein:The
No.e1620. structureofE.coliadenylatekinasewithboundAMPandAMPPNP.
(19) Takada, S. Go̅ model revisited. Biophys. Physicobiol. 2019, 16, Proteins:Struct.,Funct.,Bioinf.1994,19,183−198.
248−255. (39) Müller, C.; Schlauderer, G. J.; Reinstein, J.; Schulz, G. E.
(20)Okazaki,K.I.;Koga,N.;Takada,S.;Onuchic,J.N.;Wolynes,P. Adenylatekinasemotionsduringcatalysis:Anenergeticcounterweight
G. Multiple-basin energy landscapes for large-amplitude conforma- balancingsubstratebinding.Structure1996,4,147−156.
|     |     |     |     |     |     | 2627 |     |     |     |     | https://doi.org/10.1021/acs.jctc.3c01222 |     |     |     |
| --- | --- | --- | --- | --- | --- | ---- | --- | --- | --- | --- | ---------------------------------------- | --- | --- | --- |
J.Chem.TheoryComput.2024,20,2618−2629

JournalofChemicalTheoryandComputation pubs.acs.org/JCTC Article
(40)Henzler-Wildman,K.A.;Thai,V.;Lei,M.;Ott,M.;Wolf-Watz, (58)Buyan,A.;Cox,C.D.;Barnoud,J.;Li,J.;Chan,H.S.;Martinac,
M.;Fenn,T.;Pozharski,E.;Wilson,M.A.;Petsko,G.A.;Karplus,M.; B.; Marrink, S. J.; Corry, B. Piezo1 Forms Specific, Functionally
Hübner,C.G.;Kern,D.Intrinsicmotionsalonganenzymaticreaction Important Interactions with Phosphoinositides and Cholesterol.
trajectory.Nature2007,450,838−844. Biophys.J.2020,119,1683−1697.
(41)Li,W.;Wolynes,P.G.;Takada,S.Frustration,specificsequence (59)Mosalaganti,S.;Obarska-Kosinska,A.;Siggel,M.;Taniguchi,R.;
dependence, and nonlinearity in large-amplitude fluctuations of Turoňová,B.;Zimmerli,C.E.;Buczak,K.;Schmidt,F.H.;Margiotta,
allostericproteins.Proc.Natl.Acad.Sci.U.S.A.2011,108,3504−3509. E.;Mackmull,M.T.;Hagen,W.J.;Hummer,G.;Kosinski,J.;Beck,M.
(42)Stiller,J.B.;JordanKerns,S.;Hoemberger,M.;Cho,Y.J.;Otten, AI-basedstructurepredictionempowersintegrativestructuralanalysis
R.; Hagan, M. F.; Kern, D. Probing the transition state in enzyme ofhumannuclearpores.Science2022,376,No.eabm9506.
catalysisbyhigh-pressureNMRdynamics.Nat.Catal.2019,2,726− (60)Schlitter,J.;Engels,M.;Krüger,P.Targetedmoleculardynamics:
734. Anewapproachforsearchingpathwaysofconformationaltransitions.J.
(43) Seyler, S. L.; Beckstein, O. Sampling large conformational Mol.Graph.1994,12,84−89.
transitions:Adenylatekinaseasatestingground.Mol.Simul.2014,40, (61)Wassenaar,T.A.;Pluhackova,K.;Böckmann,R.A.;Marrink,S.
855−877. J.;Tieleman,D.P.GoingBackward:AFlexibleGeometricApproachto
(44) Kobayashi, C.; Matsunaga, Y.; Koike, R.; Ota, M.; Sugita, Y. ReverseTransformationfromCoarseGrainedtoAtomisticModels.J.
Domain Motion Enhanced (DoME) Model for Efficient Conforma- Chem.TheoryComput.2014,10,676−690.
tionalSamplingofMultidomainProteins.J.Phys.Chem.B2015,119, (62)Vickery,O.N.;Stansfeld,P.J.CG2AT2:anEnhancedFragment-
14584−14593. Based Approach for Serial Multi-scale Molecular Dynamics Simu-
(45) Barisione, G.; Baroffio, M.; Crimi, E.; Brusasco, V. Beta- lations.J.Chem.TheoryComput.2021,17,6472−6482.
adrenergicagonists.Pharmaceuticals2010,3,1016−1044. (63) Maragliano, L.; Fischer, A.; Vanden-Eijnden, E.; Ciccotti, G.
(46)Rasmussen,S.G.;Devree,B.T.;Zou,Y.;Kruse,A.C.;Chung,K. Stringmethodincollectivevariables:Minimumfreeenergypathsand
Y.;Kobilka,T.S.;Thian,F.S.;Chae,P.S.;Pardon,E.;Calinski,D.; isocommittorsurfaces.J.Chem.Phys.2006,125,024106.
Mathiesen,J.M.;Shah,S.T.;Lyons,J.A.;Caffrey,M.;Gellman,S.H.; (64)Casalino,L.;Gaieb,Z.;Goldsmith,J.A.;Hjorth,C.K.;Dommer,
Steyaert,J.;Skiniotis,G.;Weis,W.I.;Sunahara,R.K.;Kobilka,B.K. A. C.; Harbison, A. M.; Fogarty, C. A.; Barros, E. P.; Taylor, B. C.;
Crystal structure of the β adrenergic receptor-Gs protein complex. McLellan,J.S.;etal.BeyondShielding:TheRolesofGlycansinthe
2
Nature2011,477,549−555. SARS-CoV-2SpikeProtein.ACSCent.Sci.2020,6,1722−1734.
(47)Cherezov,V.;Rosenbaum,D.M.;Hanson,M.A.;Rasmussen,S. (65)Mori,T.;Jung,J.;Kobayashi,C.;Dokainish,H.M.;Re,S.;Sugita,
G.; Thian, F. S.; Kobilka, T. S.; Choi, H. J.; Kuhn, P.; Weis, W. I.; Y. Elucidation of interactions regulating conformational stability and
Kobilka,B.K.;Stevens, R. C.High-resolution crystal structureof an dynamicsofSARS-CoV-2S-protein.Biophys.J.2021,120,1060−1071.
engineered human β-adrenergic G protein-coupled receptor. Science (66) Panthi, B.; Dutta, S.; Chandra, A. All-atom simulations of the
2
2007,318,1258−1265. trimericspikeproteinofSARS-CoV-2inaqueousmedium:Natureof
(48)Dror,R.O.;Arlow,D.H.;Maragakis,P.;Mildorf,T.J.;Pan,A. interactions, conformational stability and free energy diagrams for
C.;Xu,H.;Borhani,D.W.;Shaw,D.E.Activationmechanismoftheβ- conformational transition of the protein. J. Comput. Chem. 2023, 44,
2
adrenergic receptor. Proc. Natl. Acad. Sci. U.S.A. 2011, 108, 18684− 1560−1577.
18689. (67)Gur,M.;Taka,E.;Yilmaz,S.Z.;Kilinc,C.;Aktas,U.;Golcuk,M.
(49) Kohlhoff, K. J.; Shukla, D.; Lawrenz, M.; Bowman, G. R.; ConformationaltransitionofSARS-CoV-2spikeglycoproteinbetween
Konerding,D.E.;Belov,D.;Altman,R.B.;Pande,V.S.Cloud-based itsclosedandopenstates.J.Chem.Phys.2020,153,075101.
simulations on Google Exacycle reveal ligand modulation of GPCR (68) Bhattacharjee, S.; Feng, X.; Maji, S.; Dadhwal, P.; Zhang, Z.;
activationpathways.Nat.Chem.2014,6,15−21. Brown, Z. P.; Frank, J. Time resolution in cryo-EM using a PDMS-
(50)Montigny,C.;Lyons,J.;Champeil,P.;Nissen,P.;Lenoir,G.On based microfluidic chip assembly and its application to the study of
the molecular mechanism of flippase- and scramblase-mediated HflX-mediatedribosomerecycling.Cell2024,187,782−796.e23.
phospholipid transport. Biochim. Biophys. Acta, Mol. Cell Biol. Lipids (69) Wayment-Steele, H. K.; Ojoawo, A.; Otten, R.; Apitz, J. M.;
2016,1861,767−783. Pitsawong,W.;Hömberger,M.;Ovchinnikov,S.;Colwell,L.;Kern,D.
(51) López-Marqués, R. L.; Gourdon, P.; Günther Pomorski, T.; Predicting multiple conformations via sequence clustering and
Palmgren,M.ThetransportmechanismofP4ATPaselipidflippases. AlphaFold2.Nature2023,625,832−839.
Biochem.J.2020,477,3769−3790. (70) Li, J.; Wang, L.; Zhu, Z.; Song, C. Exploring the Alternative
(52)Hiraizumi,M.;Yamashita,K.;Nishizawa,T.;Nureki,O.Cryo- ConformationofaKnownProteinStructureBasedonContactMap
EMstructurescapturethetransportcycleoftheP4-ATPaseflippase. Prediction.J.Chem.Inf.Model.2024,64,301−315.
Science2019,365,1149−1155. (71)Pedersen,K.B.;Borges-Arauj́o,L.;Stange,A.D.;Souza,P.C.T.;
(53)Bai,L.;You,Q.;Jain,B.K.;Duan,H.D.;Kovach,A.;Graham,T. Marrink, S.-J.; Schiøtt, B. OLIVES: A Go-like Model for Stabilizing
R.; Li, H. Transport mechanism of P4 ATPase phosphatidylcholine Protein Structure via Hydrogen Bonding Native Contacts in the
flippases.eLife2020,9,No.e62163. Martini3Coarse-GrainedForceField.ChemRxiv2023.
(54) Xu, J.; He, Y.; Wu, X.; Li, L. Conformational changes of a (72) Best, R. B.; Chen, Y. G.; Hummer, G. Slow protein
phosphatidylcholine flippase in lipid membranes. Cell Rep. 2022, 38, conformationaldynamicsfrommultipleexperimentalstructures:The
110518. helix/sheettransitionofArcrepressor.Structure2005,13,1755−1763.
(55) He, Y.; Xu, J.; Wu, X.; Li, L. Structures of a P4-ATPase lipid (73) Abraham, M. J.; Murtola, T.; Schulz, R.;Páll, S.; Smith, J. C.;
flippaseinlipidbilayers.ProteinandCell2020,11,458−463. Hess, B.; Lindahl, E. Gromacs: High performance molecular
(56)Vestergaard,A.L.;Coleman,J.A.;Lemmin,T.;Mikkelsen,S.A.; simulations through multi-level parallelism from laptops to super-
Molday,L.L.;Vilsen,B.;Molday,R.S.;DalPeraro,M.;Andersen,J.P. computers.SoftwareX2015,1−2,19−25.
Criticalrolesofisoleucine-364andadjacentresiduesinahydrophobic (74) Bussi, G.; Donadio, D.; Parrinello, M. Canonical sampling
gatecontrolofphospholipidtransportbythemammalianP4-ATPase throughvelocityrescaling.J.Chem.Phys.2007,126,014101.
ATP8A2.Proc.Natl.Acad.Sci.U.S.A.2014,111,E1334−E1343. (75) Parrinello, M.; Rahman, A. Polymorphic transitions in single
(57)Klomp,L.W.;Vargas,J.C.;vanMil,S.W.C.;Pawlikowska,L.; crystals:Anewmoleculardynamicsmethod.J. Appl.Phys.1981,52,
Strautnieks,S.S.;vanEijk,M.J.T.;Juijn,J.A.;Pabón-Peña,C.;Smith, 7182−7190.
L.B.;DeYoung,J.A.;Byrne,J.A.;Gombert,J.;vanderBrugge,G.; (76) Tironi, I. G.; Sperb, R.; Smith, P. E.; van Gunsteren, W. F. A
Berger, R.; Jankowska, I.; Pawlowska, J.; Villa, E.; Knisely, A. S.; generalizedreactionfieldmethodformoleculardynamicssimulations.
Thompson, R. J.; Freimer, N. B.; Houwen, R. H.; Bull, L. N. J.Chem.Phys.1995,102,5451−5459.
Characterization of mutations in ATP8B1 associated with hereditary (77)Wassenaar,T.A.;Ingólfsson,H.I.;Böckmann,R.A.;Tieleman,
cholestasis.Hepatology2004,40,27−38. D.P.;Marrink,S.J.Computationallipidomicswithinsane:Aversatile
2628 https://doi.org/10.1021/acs.jctc.3c01222
J.Chem.TheoryComput.2024,20,2618−2629

JournalofChemicalTheoryandComputation pubs.acs.org/JCTC Article
tool for generating custom membranes for molecular simulations. J.
Chem.TheoryComput.2015,11,2144−2155.
(78) Šali, A.; Blundell, T. L. Comparative protein modelling by
satisfactionofspatialrestraints.J.Mol.Biol.1993,234,779−815.
(79)Humphrey,W.;Dalke,A.;Schulten,K.VMD:Visualmolecular
dynamics.J.Mol.Graph.1996,14,33−38.
(80)Michaud-Agrawal,N.;Denning,E.J.;Woolf,T.B.;Beckstein,O.
MDAnalysis: A toolkit for the analysis of molecular dynamics
simulations.J.Comput.Chem.2011,32,2319−2327.
(81) Pettersen, E. F.; Goddard, T. D.; Huang, C. C.; Meng, E. C.;
Couch,G.S.;Croll,T.I.;Morris,J.H.;Ferrin,T.E.UCSFChimeraX:
Structure visualization for researchers, educators, and developers.
ProteinSci.2021,30,70−82.
2629 https://doi.org/10.1021/acs.jctc.3c01222
J.Chem.TheoryComput.2024,20,2618−2629
