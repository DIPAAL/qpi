"""Enums for the available ENC cells."""
from enum import Enum


class EncCell(str, Enum):
    """Enum of available ENC cells."""

    dipaal_spatial_domain = "DIPAAL Spatial Domain"
    aabenraa = "Aabenraa"
    aabenraa_havn = "Aabenraa Havn"
    aalborg_oesthavn = "Aalborg Østhavn"
    arkona_bis_kolberg = "Arkona Bis Kolberg"
    asnaesvaerket = "Asnæsværket"
    avedoerevaerket = "Avedøreværket"
    baelthavet = "Bælthavet"
    christiansoe = "Christiansø"
    danmark_med_omgivende_farvande = "Danmark med omgivende farvande"
    danmark_soegraenser = "Danmark, Søgrænser"
    danmarks_eksklusive_oekonomiske_zone = "Danmarks eksklusive økonomiske zone"
    danmarks_territoriale_farvand = "Danmarks territoriale farvand"
    danmarks_tilstoedende_zone = "Danmarks tilstødende zone"
    egholm = "Egholm"
    ensted = "Ensted"
    esbjerg_havn = "Esbjerg Havn"
    esbjerg_nord = "Esbjerg Nord"
    esbjerg_syd = "Esbjerg Syd"
    farvandet_syd_for_fyn_rudkoebing_loeb = "Farvandet syd for Fyn. Rudkøbing Løb"
    farvandet_syd_for_fyn_svendborg_sund = "Farvandet syd for Fyn. Svendborg Sund"
    flintrannan = "Flintrännan"
    fredericia = "Fredericia"
    fredericia_vest = "Fredericia Vest"
    fredericia_oest = "Fredericia Øst"
    frederikshavn = "Frederikshavn"
    frederikshavn_1 = "Frederikshavn_1"
    frederiksvaerk = "Frederiksværk"
    frederiksvaerk_staalvalsevaerks_havn = "Frederiksværk Stålvalseværks Havn"
    frederiksvaerk_kajnumre = "Frederiksværk kajnumre"
    fynsvaerket = "Fynsværket"
    gabelsflach_bis_fehmarnsund = "Gabelsflach Bis Fehmarnsund"
    gennemsejling_ved_sletterhage = "Gennemsejling ved Sletterhage"
    grenaa = "Grenaa"
    hanstholm = "Hanstholm"
    hanstholm_havn = "Hanstholm Havn"
    hanstholm_kajnumre = "Hanstholm kajnumre"
    helsingborg_olands_sodra_udde = "Helsingborg - Ölands Södra Udde"
    helsingoer__helsingborg = "Helsingør - Helsingborg"
    hirtshals = "Hirtshals"
    hvide_sande = "Hvide Sande"
    indsejling_til_faaborg = "Indsejling til Faaborg"
    indsejling_til_frederikshavn = "Indsejling til Frederikshavn"
    indsejling_til_gedser = "Indsejling til Gedser"
    indsejling_til_grenaa = "Indsejling til Grenaa"
    indsejling_til_hals = "Indsejling til Hals"
    indsejling_til_koege = "Indsejling til Køge"
    indsejling_til_marstal = "Indsejling til Marstal"
    indsejling_til_nyborg = "Indsejling til Nyborg"
    indsejling_til_skaelskoer = "Indsejling til Skælskør"
    indsejling_til_vordingborg = "Indsejling til Vordingborg"
    indsejling_til_aeroeskoebing = "Indsejling til Ærøskøbing"
    indsejlingen_til_esbjerg = "Indsejlingen til Esbjerg"
    kaeften = "Kaeften"
    kalundborg = "Kalundborg"
    kalundborg_havn = "Kalundborg Havn"
    kasserodde_flak = "Kasserodde Flak"
    kattegat = "Kattegat"
    kattegat_nlige_del = "Kattegat, N-lige del"
    kattegat_slige_del = "Kattegat, S-lige del"
    kattegat_selige_del = "Kattegat, SE-lige del"
    kattegat_aarhus_havn = "Kattegat. Aarhus Havn"
    kattegat_farvandet_nord_for_fyn = "Kattegat. Farvandet nord for Fyn"
    kattegat_horsens_fjord = "Kattegat. Horsens Fjord"
    kattegat_isefjord = "Kattegat. Isefjord"
    kattegat_laesoe_rende = "Kattegat. Læsø Rende"
    kattegat_mariager_fjord = "Kattegat. Mariager Fjord"
    kattegat_odense_fjord = "Kattegat. Odense Fjord"
    kattegat_randers_fjord = "Kattegat. Randers Fjord"
    kattegat_roskilde_fjord_frederikssund__roskilde = "Kattegat. Roskilde Fjord, Frederikssund - Roskilde"
    kattegat_roskilde_fjord_lynaes_frederikssund = "Kattegat. Roskilde Fjord, Lynæs - Frederikssund"
    kattegat_s_for_anholt = "Kattegat. S for Anholt"
    kattegat_samsoe_baelt = "Kattegat. Samsø Bælt"
    kattegat_aalborg_bugt = "Kattegat. Ålborg Bugt"
    kattegat_aalbaek_bugt = "Kattegat. Ålbæk Bugt"
    kattegat_aarhus_bugt = "Kattegat. Århus Bugt"
    kattegatt = "Kattegatt"
    kolding_havn = "Kolding Havn"
    korsoer = "Korsør"
    koebenhavns_havn_sydlige_del = "Københavns Havn (Sydlige del)"
    koebenhavns_havn_lille = "Københavns Havn Lille"
    koebenhavns_havn_stor = "Københavns Havn Stor"
    koebenhavns_havn_sikringsomraader = "Københavns Havn sikringsområder"
    koege_havn = "Køge Havn"
    lillebaelt_nlige_del = "Lillebælt, N-lige del"
    lillebaelt_slige_del_og_farvandet_syd_for_fyn = "Lillebælt, S-lige del og Farvandet syd for Fyn"
    lillebaelt_aabenraa_fjord = "Lillebælt. Aabenraa Fjord"
    lillebaelt_als_sund_og_soenderborg_bugt = "Lillebælt. Als Sund og Sønderborg Bugt"
    lillebaelt_flensborg_fjord = "Lillebælt. Flensborg Fjord"
    lillebaelt_haderslev_fjord = "Lillebælt. Haderslev Fjord"
    lillebaelt_snaevringen_og_kolding_fjord = "Lillebælt. Snævringen og Kolding Fjord"
    lillebaelt_vejle_fjord = "Lillebælt. Vejle Fjord"
    lillegrund_n = "Lillegrund N"
    limfjorden_aalborg__loegstoer = "Limfjorden. Aalborg - Løgstør"
    limfjorden_aalborg_havn = "Limfjorden. Aalborg Havn"
    limfjorden_hals__aalborg = "Limfjorden. Hals - Aalborg"
    limfjorden_mors__loegstoer = "Limfjorden. Mors - Løgstør"
    limfjorden_thyboroen__mors = "Limfjorden. Thyborøn - Mors"
    lindholm_og_avernakke_terminalerne = "Lindholm og Avernakke Terminalerne"
    laesoe_rende = "Læsø Rende"
    masnedsund = "Masnedsund"
    nakkeboelle_fjord = "Nakkebølle Fjord"
    nakskov = "Nakskov"
    nordsoeen_blaavands_huk__fanoe = "Nordsøen. Blåvands Huk - Fanø"
    nordsoeen_fanoe__sylt = "Nordsøen. Fanø - Sylt"
    nordsoeen_graadyb = "Nordsøen. Grådyb"
    nordsoeen_horns_rev = "Nordsøen. Horns Rev"
    nordsoeen_ringkoebing_fjord = "Nordsøen. Ringkøbing Fjord"
    norsoeen_helgoland_til_roemoe = "Norsøen, Helgoland til Rømø"
    nykoebing_f = "Nykøbing F"
    odense_havn__inderhavnen = "Odense Havn - Inderhavnen"
    odense_havnlindoe = "Odense Havn-Lindø"
    odense_havnlindoe_slige_del = "Odense Havn-Lindø  S-lige del"
    odense_havnlindoe_nlige_del = "Odense Havn-Lindø N-lige del"
    roedbyhavn = "Rødbyhavn"
    roenne = "Rønne"
    skagen = "Skagen"
    skagerak = "Skagerak"
    skagerrak = "Skagerrak"
    smaalandsfarvandet_nelige_del = "Smålandsfarvandet, NE-lige del"
    smaalandsfarvandet_selige_del = "Smålandsfarvandet, SE-lige del"
    smaalandsfarvandet_wlige_del = "Smålandsfarvandet, W-lige del"
    smaalandsfarvandet_guldbord_sund = "Smålandsfarvandet. Guldbord Sund"
    smaalandsfarvandet_karrebaek_fjord = "Smålandsfarvandet. Karrebæk Fjord"
    storebaelt_nlige_del = "Storebælt, N-lige del"
    storebaelt_slige_del = "Storebælt, S-lige del"
    storebaelt_kalundborg_fjord = "Storebælt. Kalundborg Fjord"
    storebaelt_nakskov_fjord = "Storebælt. Nakskov Fjord"
    storebaelt_sprogoe__langeland = "Storebælt. Sprogø - Langeland"
    studstrupvaerket = "Studstrupværket"
    sundet_nlige_del = "Sundet, N-lige del"
    sundet_nlige_del__sundet_northern_part = "Sundet, N-lige del / Sundet, Northern Part"
    sundet_slige_del = "Sundet, S-lige del"
    sundet_midterste_del = "Sundet, midterste del"
    sundet_koebenhavns_havn = "Sundet. Københavns Havn"
    soenderborg = "Sønderborg"
    thyboroen_kanal = "Thyborøn Kanal"
    venoe_sund_snaevring = "Venø Sund Snævring"
    vordingborg_havne = "Vordingborg Havne"
    vordingborg_sydhavn = "Vordingborg Sydhavn"
    oeer_havn = "Øer Havn"
    oeresundsbroen = "Øresundsbroen"
    oestbroen__east_bridge = "Østbroen - East Bridge"
    oestersoeen_omkring_bornholm = "Østersøen omkring Bornholm"
    oestersoeen_wlige_del = "Østersøen, W-lige del"
    oestersoeen_bornholmsgat = "Østersøen. Bornholmsgat"
    oestersoeen_faxe_bugt_og_hjelm_bugt = "Østersøen. Faxe Bugt og Hjelm Bugt"
    oestersoeen_faxe_bugt_og_praestoe_fjord = "Østersøen. Faxe Bugt og Præstø Fjord"
    oestersoeen_femern_baelt = "Østersøen. Femern Bælt"
    oestersoeen_femern_baelt__sundet = "Østersøen. Femern Bælt - Sundet"
    oestersoeen_femern_baelt_1 = "Østersøen. Femern Bælt_1"
    oestersoeen_gedser_rev_og_kadetrenden = "Østersøen. Gedser Rev og Kadetrenden"
