"""
btable.py - the bearing table. 

An example of a bearing table from a Tritech
Gemini GLF file. This apparently doesn't change at 
all expect perhaps between different models of
sonar, but is included on every record for some
reason. """

from numba.typed import List as NumbaList

# TODO - this seems to suggest the lefthand of the image is in the postive
# angle direction which is opposite to PAMGuard and our pipeline ><

bearing_table = NumbaList([
    1.0471975803375244,
    1.0404577255249023,
    1.033794641494751,
    1.0272051095962524,
    1.0206868648529053,
    1.0142370462417603,
    1.007853388786316,
    1.0015337467193604,
    0.9952758550643921,
    0.9890778064727783,
    0.9829375743865967,
    0.9768534302711487,
    0.9708235859870911,
    0.9648464918136597,
    0.9589204788208008,
    0.953044056892395,
    0.9472159147262573,
    0.9414345622062683,
    0.9356988072395325,
    0.93000727891922,
    0.9243589043617249,
    0.9187524914741516,
    0.9131869673728943,
    0.9076611995697021,
    0.9021742939949036,
    0.8967252373695374,
    0.8913131356239319,
    0.885936975479126,
    0.8805960416793823,
    0.8752893805503845,
    0.8700162768363953,
    0.8647759556770325,
    0.8595675826072693,
    0.854390561580658,
    0.8492441177368164,
    0.8441275954246521,
    0.8390403389930725,
    0.8339818120002747,
    0.8289512395858765,
    0.8239482045173645,
    0.8189719915390015,
    0.8140221834182739,
    0.8090981841087341,
    0.8041994571685791,
    0.7993255257606506,
    0.7944758534431458,
    0.7896500825881958,
    0.7848476767539978,
    0.7800681591033936,
    0.7753111720085144,
    0.7705762386322021,
    0.7658630013465881,
    0.7611709833145142,
    0.7564998865127563,
    0.7518492937088013,
    0.7472187876701355,
    0.7426081299781799,
    0.7380168437957764,
    0.7334446907043457,
    0.7288912534713745,
    0.7243562936782837,
    0.7198394536972046,
    0.7153404355049133,
    0.7108588814735413,
    0.706394612789154,
    0.7019472718238831,
    0.6975166201591492,
    0.6931023001670837,
    0.6887041330337524,
    0.6843218803405762,
    0.6799551844596863,
    0.6756038665771484,
    0.6712676882743835,
    0.6669463515281677,
    0.6626396775245667,
    0.6583474278450012,
    0.6540694236755371,
    0.6498053669929504,
    0.6455550789833069,
    0.6413183808326721,
    0.637095034122467,
    0.6328848004341125,
    0.6286875605583191,
    0.6245031356811523,
    0.6203312277793884,
    0.6161717772483826,
    0.6120244860649109,
    0.6078892946243286,
    0.6037659049034119,
    0.5996542572975159,
    0.5955540537834167,
    0.5914652943611145,
    0.5873876810073853,
    0.5833211541175842,
    0.5792654752731323,
    0.5752205848693848,
    0.5711861848831177,
    0.567162275314331,
    0.5631486773490906,
    0.5591451525688171,
    0.5551517009735107,
    0.5511680841445923,
    0.5471941828727722,
    0.543229877948761,
    0.539275050163269,
    0.5353295803070068,
    0.5313933491706848,
    0.5274661183357239,
    0.5235479474067688,
    0.5196385383605957,
    0.5157378911972046,
    0.5118458271026611,
    0.5079622864723206,
    0.5040870904922485,
    0.5002201795578003,
    0.4963614344596863,
    0.49251073598861694,
    0.48866796493530273,
    0.4848330318927765,
    0.48100581765174866,
    0.47718626260757446,
    0.47337421774864197,
    0.469569593667984,
    0.4657723009586334,
    0.46198225021362305,
    0.4581993520259857,
    0.4544234871864319,
    0.4506545662879944,
    0.44689252972602844,
    0.4431372284889221,
    0.439388632774353,
    0.4356466233730316,
    0.4319111406803131,
    0.42818203568458557,
    0.424459308385849,
    0.42074280977249146,
    0.41703248023986816,
    0.41332826018333435,
    0.40963003039360046,
    0.40593773126602173,
    0.40225130319595337,
    0.39857062697410583,
    0.39489564299583435,
    0.39122629165649414,
    0.38756248354911804,
    0.3839041590690613,
    0.3802511990070343,
    0.3766036033630371,
    0.37296122312545776,
    0.36932405829429626,
    0.36569198966026306,
    0.36206498742103577,
    0.35844293236732483,
    0.35482579469680786,
    0.3512135148048401,
    0.34760597348213196,
    0.34400317072868347,
    0.34040501713752747,
    0.3368114233016968,
    0.333222359418869,
    0.329637736082077,
    0.3260575234889984,
    0.322481632232666,
    0.31891000270843506,
    0.31534257531166077,
    0.31177929043769836,
    0.30822011828422546,
    0.3046649396419525,
    0.3011137545108795,
    0.2975664734840393,
    0.2940230667591095,
    0.2904834449291229,
    0.2869475483894348,
    0.2834153473377228,
    0.27988678216934204,
    0.2763617932796478,
    0.27284032106399536,
    0.26932233572006226,
    0.26580774784088135,
    0.26229649782180786,
    0.2587885856628418,
    0.255283921957016,
    0.25178244709968567,
    0.24828413128852844,
    0.24478891491889954,
    0.24129673838615417,
    0.23780757188796997,
    0.23432135581970215,
    0.23083803057670593,
    0.22735755145549774,
    0.2238798886537552,
    0.2204049676656723,
    0.2169327437877655,
    0.2134631872177124,
    0.20999622344970703,
    0.2065318375825882,
    0.20306995511054993,
    0.19961053133010864,
    0.19615353643894196,
    0.1926989108324051,
    0.18924662470817566,
    0.1857966035604477,
    0.18234883248806,
    0.1789032369852066,
    0.17545980215072632,
    0.17201845347881317,
    0.16857917606830597,
    0.16514189541339874,
    0.1617065966129303,
    0.15827320516109467,
    0.15484170615673065,
    0.15141203999519348,
    0.14798417687416077,
    0.14455805718898773,
    0.1411336362361908,
    0.13771089911460876,
    0.13428977131843567,
    0.13087022304534912,
    0.12745222449302673,
    0.12403571605682373,
    0.12062066048383713,
    0.11720702052116394,
    0.11379475146532059,
    0.11038381606340408,
    0.10697416216135025,
    0.1035657599568367,
    0.10015856474637985,
    0.09675253927707672,
    0.09334763884544373,
    0.08994381874799728,
    0.08654104918241501,
    0.08313927799463272,
    0.07973847538232803,
    0.07633858919143677,
    0.07293959707021713,
    0.06954143941402435,
    0.06614409387111664,
    0.06274750828742981,
    0.05935164913535118,
    0.05595647171139717,
    0.05256194248795509,
    0.049168020486831665,
    0.0457746647298336,
    0.042381834238767624,
    0.03898949548602104,
    0.035597603768110275,
    0.03220612183213234,
    0.02881500869989395,
    0.025424228981137276,
    0.02203373983502388,
    0.01864350587129593,
    0.015253485180437565,
    0.011863639578223228,
    0.00847393088042736,
    0.005084319971501827,
    0.00169476680457592,
    -0.00169476680457592,
    -0.005084319971501827,
    -0.00847393088042736,
    -0.011863639578223228,
    -0.015253485180437565,
    -0.01864350587129593,
    -0.02203373983502388,
    -0.025424228981137276,
    -0.02881500869989395,
    -0.03220612183213234,
    -0.035597603768110275,
    -0.03898949548602104,
    -0.042381834238767624,
    -0.0457746647298336,
    -0.049168020486831665,
    -0.05256194248795509,
    -0.05595647171139717,
    -0.05935164913535118,
    -0.06274750828742981,
    -0.06614409387111664,
    -0.06954143941402435,
    -0.07293959707021713,
    -0.07633858919143677,
    -0.07973847538232803,
    -0.08313927799463272,
    -0.08654104918241501,
    -0.08994381874799728,
    -0.09334763884544373,
    -0.09675253927707672,
    -0.10015856474637985,
    -0.1035657599568367,
    -0.10697416216135025,
    -0.11038381606340408,
    -0.11379475146532059,
    -0.11720702052116394,
    -0.12062066048383713,
    -0.12403571605682373,
    -0.12745222449302673,
    -0.13087022304534912,
    -0.13428977131843567,
    -0.13771089911460876,
    -0.1411336362361908,
    -0.14455805718898773,
    -0.14798417687416077,
    -0.15141203999519348,
    -0.15484170615673065,
    -0.15827320516109467,
    -0.1617065966129303,
    -0.16514189541339874,
    -0.16857917606830597,
    -0.17201845347881317,
    -0.17545980215072632,
    -0.1789032369852066,
    -0.18234883248806,
    -0.1857966035604477,
    -0.18924662470817566,
    -0.1926989108324051,
    -0.19615353643894196,
    -0.19961053133010864,
    -0.20306995511054993,
    -0.2065318375825882,
    -0.20999622344970703,
    -0.2134631872177124,
    -0.2169327437877655,
    -0.2204049676656723,
    -0.2238798886537552,
    -0.22735755145549774,
    -0.23083803057670593,
    -0.23432135581970215,
    -0.23780757188796997,
    -0.24129673838615417,
    -0.24478891491889954,
    -0.24828413128852844,
    -0.25178244709968567,
    -0.255283921957016,
    -0.2587885856628418,
    -0.26229649782180786,
    -0.26580774784088135,
    -0.26932233572006226,
    -0.27284032106399536,
    -0.2763617932796478,
    -0.27988678216934204,
    -0.2834153473377228,
    -0.2869475483894348,
    -0.2904834449291229,
    -0.2940230667591095,
    -0.2975664734840393,
    -0.3011137545108795,
    -0.3046649396419525,
    -0.30822011828422546,
    -0.31177929043769836,
    -0.31534257531166077,
    -0.31891000270843506,
    -0.322481632232666,
    -0.3260575234889984,
    -0.329637736082077,
    -0.333222359418869,
    -0.3368114233016968,
    -0.34040501713752747,
    -0.34400317072868347,
    -0.34760597348213196,
    -0.3512135148048401,
    -0.35482579469680786,
    -0.35844293236732483,
    -0.36206498742103577,
    -0.36569198966026306,
    -0.36932405829429626,
    -0.37296122312545776,
    -0.3766036033630371,
    -0.3802511990070343,
    -0.3839041590690613,
    -0.38756248354911804,
    -0.39122629165649414,
    -0.39489564299583435,
    -0.39857062697410583,
    -0.40225130319595337,
    -0.40593773126602173,
    -0.40963003039360046,
    -0.41332826018333435,
    -0.41703248023986816,
    -0.42074280977249146,
    -0.424459308385849,
    -0.42818203568458557,
    -0.4319111406803131,
    -0.4356466233730316,
    -0.439388632774353,
    -0.4431372284889221,
    -0.44689252972602844,
    -0.4506545662879944,
    -0.4544234871864319,
    -0.4581993520259857,
    -0.46198225021362305,
    -0.4657723009586334,
    -0.469569593667984,
    -0.47337421774864197,
    -0.47718626260757446,
    -0.48100581765174866,
    -0.4848330318927765,
    -0.48866796493530273,
    -0.49251073598861694,
    -0.4963614344596863,
    -0.5002201795578003,
    -0.5040870904922485,
    -0.5079622864723206,
    -0.5118458271026611,
    -0.5157378911972046,
    -0.5196385383605957,
    -0.5235479474067688,
    -0.5274661183357239,
    -0.5313933491706848,
    -0.5353295803070068,
    -0.539275050163269,
    -0.543229877948761,
    -0.5471941828727722,
    -0.5511680841445923,
    -0.5551517009735107,
    -0.5591451525688171,
    -0.5631486773490906,
    -0.567162275314331,
    -0.5711861848831177,
    -0.5752205848693848,
    -0.5792654752731323,
    -0.5833211541175842,
    -0.5873876810073853,
    -0.5914652943611145,
    -0.5955540537834167,
    -0.5996542572975159,
    -0.6037659049034119,
    -0.6078892946243286,
    -0.6120244860649109,
    -0.6161717772483826,
    -0.6203312277793884,
    -0.6245031356811523,
    -0.6286875605583191,
    -0.6328848004341125,
    -0.637095034122467,
    -0.6413183808326721,
    -0.6455550789833069,
    -0.6498053669929504,
    -0.6540694236755371,
    -0.6583474278450012,
    -0.6626396775245667,
    -0.6669463515281677,
    -0.6712676882743835,
    -0.6756038665771484,
    -0.6799551844596863,
    -0.6843218803405762,
    -0.6887041330337524,
    -0.6931023001670837,
    -0.6975166201591492,
    -0.7019472718238831,
    -0.706394612789154,
    -0.7108588814735413,
    -0.7153404355049133,
    -0.7198394536972046,
    -0.7243562936782837,
    -0.7288912534713745,
    -0.7334446907043457,
    -0.7380168437957764,
    -0.7426081299781799,
    -0.7472187876701355,
    -0.7518492937088013,
    -0.7564998865127563,
    -0.7611709833145142,
    -0.7658630013465881,
    -0.7705762386322021,
    -0.7753111720085144,
    -0.7800681591033936,
    -0.7848476767539978,
    -0.7896500825881958,
    -0.7944758534431458,
    -0.7993255257606506,
    -0.8041994571685791,
    -0.8090981841087341,
    -0.8140221834182739,
    -0.8189719915390015,
    -0.8239482045173645,
    -0.8289512395858765,
    -0.8339818120002747,
    -0.8390403389930725,
    -0.8441275954246521,
    -0.8492441177368164,
    -0.854390561580658,
    -0.8595675826072693,
    -0.8647759556770325,
    -0.8700162768363953,
    -0.8752893805503845,
    -0.8805960416793823,
    -0.885936975479126,
    -0.8913131356239319,
    -0.8967252373695374,
    -0.9021742939949036,
    -0.9076611995697021,
    -0.9131869673728943,
    -0.9187524914741516,
    -0.9243589043617249,
    -0.93000727891922,
    -0.9356988072395325,
    -0.9414345622062683,
    -0.9472159147262573,
    -0.953044056892395,
    -0.9589204788208008,
    -0.9648464918136597,
    -0.9708235859870911,
    -0.9768534302711487,
    -0.9829375743865967,
    -0.9890778064727783,
    -0.9952758550643921,
    -1.0015337467193604,
    -1.007853388786316,
    -1.0142370462417603,
    -1.0206868648529053,
    -1.0272051095962524,
    -1.033794641494751,
    -1.0404577255249023,
    -1.0471975803375244,
])

_bearing_table = [
    1.0471975803375244,
    1.0404577255249023,
    1.033794641494751,
    1.0272051095962524,
    1.0206868648529053,
    1.0142370462417603,
    1.007853388786316,
    1.0015337467193604,
    0.9952758550643921,
    0.9890778064727783,
    0.9829375743865967,
    0.9768534302711487,
    0.9708235859870911,
    0.9648464918136597,
    0.9589204788208008,
    0.953044056892395,
    0.9472159147262573,
    0.9414345622062683,
    0.9356988072395325,
    0.93000727891922,
    0.9243589043617249,
    0.9187524914741516,
    0.9131869673728943,
    0.9076611995697021,
    0.9021742939949036,
    0.8967252373695374,
    0.8913131356239319,
    0.885936975479126,
    0.8805960416793823,
    0.8752893805503845,
    0.8700162768363953,
    0.8647759556770325,
    0.8595675826072693,
    0.854390561580658,
    0.8492441177368164,
    0.8441275954246521,
    0.8390403389930725,
    0.8339818120002747,
    0.8289512395858765,
    0.8239482045173645,
    0.8189719915390015,
    0.8140221834182739,
    0.8090981841087341,
    0.8041994571685791,
    0.7993255257606506,
    0.7944758534431458,
    0.7896500825881958,
    0.7848476767539978,
    0.7800681591033936,
    0.7753111720085144,
    0.7705762386322021,
    0.7658630013465881,
    0.7611709833145142,
    0.7564998865127563,
    0.7518492937088013,
    0.7472187876701355,
    0.7426081299781799,
    0.7380168437957764,
    0.7334446907043457,
    0.7288912534713745,
    0.7243562936782837,
    0.7198394536972046,
    0.7153404355049133,
    0.7108588814735413,
    0.706394612789154,
    0.7019472718238831,
    0.6975166201591492,
    0.6931023001670837,
    0.6887041330337524,
    0.6843218803405762,
    0.6799551844596863,
    0.6756038665771484,
    0.6712676882743835,
    0.6669463515281677,
    0.6626396775245667,
    0.6583474278450012,
    0.6540694236755371,
    0.6498053669929504,
    0.6455550789833069,
    0.6413183808326721,
    0.637095034122467,
    0.6328848004341125,
    0.6286875605583191,
    0.6245031356811523,
    0.6203312277793884,
    0.6161717772483826,
    0.6120244860649109,
    0.6078892946243286,
    0.6037659049034119,
    0.5996542572975159,
    0.5955540537834167,
    0.5914652943611145,
    0.5873876810073853,
    0.5833211541175842,
    0.5792654752731323,
    0.5752205848693848,
    0.5711861848831177,
    0.567162275314331,
    0.5631486773490906,
    0.5591451525688171,
    0.5551517009735107,
    0.5511680841445923,
    0.5471941828727722,
    0.543229877948761,
    0.539275050163269,
    0.5353295803070068,
    0.5313933491706848,
    0.5274661183357239,
    0.5235479474067688,
    0.5196385383605957,
    0.5157378911972046,
    0.5118458271026611,
    0.5079622864723206,
    0.5040870904922485,
    0.5002201795578003,
    0.4963614344596863,
    0.49251073598861694,
    0.48866796493530273,
    0.4848330318927765,
    0.48100581765174866,
    0.47718626260757446,
    0.47337421774864197,
    0.469569593667984,
    0.4657723009586334,
    0.46198225021362305,
    0.4581993520259857,
    0.4544234871864319,
    0.4506545662879944,
    0.44689252972602844,
    0.4431372284889221,
    0.439388632774353,
    0.4356466233730316,
    0.4319111406803131,
    0.42818203568458557,
    0.424459308385849,
    0.42074280977249146,
    0.41703248023986816,
    0.41332826018333435,
    0.40963003039360046,
    0.40593773126602173,
    0.40225130319595337,
    0.39857062697410583,
    0.39489564299583435,
    0.39122629165649414,
    0.38756248354911804,
    0.3839041590690613,
    0.3802511990070343,
    0.3766036033630371,
    0.37296122312545776,
    0.36932405829429626,
    0.36569198966026306,
    0.36206498742103577,
    0.35844293236732483,
    0.35482579469680786,
    0.3512135148048401,
    0.34760597348213196,
    0.34400317072868347,
    0.34040501713752747,
    0.3368114233016968,
    0.333222359418869,
    0.329637736082077,
    0.3260575234889984,
    0.322481632232666,
    0.31891000270843506,
    0.31534257531166077,
    0.31177929043769836,
    0.30822011828422546,
    0.3046649396419525,
    0.3011137545108795,
    0.2975664734840393,
    0.2940230667591095,
    0.2904834449291229,
    0.2869475483894348,
    0.2834153473377228,
    0.27988678216934204,
    0.2763617932796478,
    0.27284032106399536,
    0.26932233572006226,
    0.26580774784088135,
    0.26229649782180786,
    0.2587885856628418,
    0.255283921957016,
    0.25178244709968567,
    0.24828413128852844,
    0.24478891491889954,
    0.24129673838615417,
    0.23780757188796997,
    0.23432135581970215,
    0.23083803057670593,
    0.22735755145549774,
    0.2238798886537552,
    0.2204049676656723,
    0.2169327437877655,
    0.2134631872177124,
    0.20999622344970703,
    0.2065318375825882,
    0.20306995511054993,
    0.19961053133010864,
    0.19615353643894196,
    0.1926989108324051,
    0.18924662470817566,
    0.1857966035604477,
    0.18234883248806,
    0.1789032369852066,
    0.17545980215072632,
    0.17201845347881317,
    0.16857917606830597,
    0.16514189541339874,
    0.1617065966129303,
    0.15827320516109467,
    0.15484170615673065,
    0.15141203999519348,
    0.14798417687416077,
    0.14455805718898773,
    0.1411336362361908,
    0.13771089911460876,
    0.13428977131843567,
    0.13087022304534912,
    0.12745222449302673,
    0.12403571605682373,
    0.12062066048383713,
    0.11720702052116394,
    0.11379475146532059,
    0.11038381606340408,
    0.10697416216135025,
    0.1035657599568367,
    0.10015856474637985,
    0.09675253927707672,
    0.09334763884544373,
    0.08994381874799728,
    0.08654104918241501,
    0.08313927799463272,
    0.07973847538232803,
    0.07633858919143677,
    0.07293959707021713,
    0.06954143941402435,
    0.06614409387111664,
    0.06274750828742981,
    0.05935164913535118,
    0.05595647171139717,
    0.05256194248795509,
    0.049168020486831665,
    0.0457746647298336,
    0.042381834238767624,
    0.03898949548602104,
    0.035597603768110275,
    0.03220612183213234,
    0.02881500869989395,
    0.025424228981137276,
    0.02203373983502388,
    0.01864350587129593,
    0.015253485180437565,
    0.011863639578223228,
    0.00847393088042736,
    0.005084319971501827,
    0.00169476680457592,
    -0.00169476680457592,
    -0.005084319971501827,
    -0.00847393088042736,
    -0.011863639578223228,
    -0.015253485180437565,
    -0.01864350587129593,
    -0.02203373983502388,
    -0.025424228981137276,
    -0.02881500869989395,
    -0.03220612183213234,
    -0.035597603768110275,
    -0.03898949548602104,
    -0.042381834238767624,
    -0.0457746647298336,
    -0.049168020486831665,
    -0.05256194248795509,
    -0.05595647171139717,
    -0.05935164913535118,
    -0.06274750828742981,
    -0.06614409387111664,
    -0.06954143941402435,
    -0.07293959707021713,
    -0.07633858919143677,
    -0.07973847538232803,
    -0.08313927799463272,
    -0.08654104918241501,
    -0.08994381874799728,
    -0.09334763884544373,
    -0.09675253927707672,
    -0.10015856474637985,
    -0.1035657599568367,
    -0.10697416216135025,
    -0.11038381606340408,
    -0.11379475146532059,
    -0.11720702052116394,
    -0.12062066048383713,
    -0.12403571605682373,
    -0.12745222449302673,
    -0.13087022304534912,
    -0.13428977131843567,
    -0.13771089911460876,
    -0.1411336362361908,
    -0.14455805718898773,
    -0.14798417687416077,
    -0.15141203999519348,
    -0.15484170615673065,
    -0.15827320516109467,
    -0.1617065966129303,
    -0.16514189541339874,
    -0.16857917606830597,
    -0.17201845347881317,
    -0.17545980215072632,
    -0.1789032369852066,
    -0.18234883248806,
    -0.1857966035604477,
    -0.18924662470817566,
    -0.1926989108324051,
    -0.19615353643894196,
    -0.19961053133010864,
    -0.20306995511054993,
    -0.2065318375825882,
    -0.20999622344970703,
    -0.2134631872177124,
    -0.2169327437877655,
    -0.2204049676656723,
    -0.2238798886537552,
    -0.22735755145549774,
    -0.23083803057670593,
    -0.23432135581970215,
    -0.23780757188796997,
    -0.24129673838615417,
    -0.24478891491889954,
    -0.24828413128852844,
    -0.25178244709968567,
    -0.255283921957016,
    -0.2587885856628418,
    -0.26229649782180786,
    -0.26580774784088135,
    -0.26932233572006226,
    -0.27284032106399536,
    -0.2763617932796478,
    -0.27988678216934204,
    -0.2834153473377228,
    -0.2869475483894348,
    -0.2904834449291229,
    -0.2940230667591095,
    -0.2975664734840393,
    -0.3011137545108795,
    -0.3046649396419525,
    -0.30822011828422546,
    -0.31177929043769836,
    -0.31534257531166077,
    -0.31891000270843506,
    -0.322481632232666,
    -0.3260575234889984,
    -0.329637736082077,
    -0.333222359418869,
    -0.3368114233016968,
    -0.34040501713752747,
    -0.34400317072868347,
    -0.34760597348213196,
    -0.3512135148048401,
    -0.35482579469680786,
    -0.35844293236732483,
    -0.36206498742103577,
    -0.36569198966026306,
    -0.36932405829429626,
    -0.37296122312545776,
    -0.3766036033630371,
    -0.3802511990070343,
    -0.3839041590690613,
    -0.38756248354911804,
    -0.39122629165649414,
    -0.39489564299583435,
    -0.39857062697410583,
    -0.40225130319595337,
    -0.40593773126602173,
    -0.40963003039360046,
    -0.41332826018333435,
    -0.41703248023986816,
    -0.42074280977249146,
    -0.424459308385849,
    -0.42818203568458557,
    -0.4319111406803131,
    -0.4356466233730316,
    -0.439388632774353,
    -0.4431372284889221,
    -0.44689252972602844,
    -0.4506545662879944,
    -0.4544234871864319,
    -0.4581993520259857,
    -0.46198225021362305,
    -0.4657723009586334,
    -0.469569593667984,
    -0.47337421774864197,
    -0.47718626260757446,
    -0.48100581765174866,
    -0.4848330318927765,
    -0.48866796493530273,
    -0.49251073598861694,
    -0.4963614344596863,
    -0.5002201795578003,
    -0.5040870904922485,
    -0.5079622864723206,
    -0.5118458271026611,
    -0.5157378911972046,
    -0.5196385383605957,
    -0.5235479474067688,
    -0.5274661183357239,
    -0.5313933491706848,
    -0.5353295803070068,
    -0.539275050163269,
    -0.543229877948761,
    -0.5471941828727722,
    -0.5511680841445923,
    -0.5551517009735107,
    -0.5591451525688171,
    -0.5631486773490906,
    -0.567162275314331,
    -0.5711861848831177,
    -0.5752205848693848,
    -0.5792654752731323,
    -0.5833211541175842,
    -0.5873876810073853,
    -0.5914652943611145,
    -0.5955540537834167,
    -0.5996542572975159,
    -0.6037659049034119,
    -0.6078892946243286,
    -0.6120244860649109,
    -0.6161717772483826,
    -0.6203312277793884,
    -0.6245031356811523,
    -0.6286875605583191,
    -0.6328848004341125,
    -0.637095034122467,
    -0.6413183808326721,
    -0.6455550789833069,
    -0.6498053669929504,
    -0.6540694236755371,
    -0.6583474278450012,
    -0.6626396775245667,
    -0.6669463515281677,
    -0.6712676882743835,
    -0.6756038665771484,
    -0.6799551844596863,
    -0.6843218803405762,
    -0.6887041330337524,
    -0.6931023001670837,
    -0.6975166201591492,
    -0.7019472718238831,
    -0.706394612789154,
    -0.7108588814735413,
    -0.7153404355049133,
    -0.7198394536972046,
    -0.7243562936782837,
    -0.7288912534713745,
    -0.7334446907043457,
    -0.7380168437957764,
    -0.7426081299781799,
    -0.7472187876701355,
    -0.7518492937088013,
    -0.7564998865127563,
    -0.7611709833145142,
    -0.7658630013465881,
    -0.7705762386322021,
    -0.7753111720085144,
    -0.7800681591033936,
    -0.7848476767539978,
    -0.7896500825881958,
    -0.7944758534431458,
    -0.7993255257606506,
    -0.8041994571685791,
    -0.8090981841087341,
    -0.8140221834182739,
    -0.8189719915390015,
    -0.8239482045173645,
    -0.8289512395858765,
    -0.8339818120002747,
    -0.8390403389930725,
    -0.8441275954246521,
    -0.8492441177368164,
    -0.854390561580658,
    -0.8595675826072693,
    -0.8647759556770325,
    -0.8700162768363953,
    -0.8752893805503845,
    -0.8805960416793823,
    -0.885936975479126,
    -0.8913131356239319,
    -0.8967252373695374,
    -0.9021742939949036,
    -0.9076611995697021,
    -0.9131869673728943,
    -0.9187524914741516,
    -0.9243589043617249,
    -0.93000727891922,
    -0.9356988072395325,
    -0.9414345622062683,
    -0.9472159147262573,
    -0.953044056892395,
    -0.9589204788208008,
    -0.9648464918136597,
    -0.9708235859870911,
    -0.9768534302711487,
    -0.9829375743865967,
    -0.9890778064727783,
    -0.9952758550643921,
    -1.0015337467193604,
    -1.007853388786316,
    -1.0142370462417603,
    -1.0206868648529053,
    -1.0272051095962524,
    -1.033794641494751,
    -1.0404577255249023,
    -1.0471975803375244,
]