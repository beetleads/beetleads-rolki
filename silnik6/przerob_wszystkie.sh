#!/bin/bash
# 13.11 22:26: ponowny montaz wszystkich zaplanowanych rolek bez smugi + kontrola ciec
cd /home/claude/silnik6
R=/home/claude/beetleads-rolki
declare -A M=([m2]=1114_0700_uchwyt_wozka [m3]=1114_1200_palec_myszka [m4]=1114_1800_abonament [z1]=1115_0700_zwrot [z2]=1115_1200_czcionka_ceny [z3]=1115_1800_doladowanie [a1]=1116_0700_szybkosc_strony [a2]=1116_1200_reklama_na_nazwe [a3]=1116_1800_pomiar_reklam [b1]=1117_0700_imie_w_mailu [b2]=1117_1200_retargeting [b3]=1117_1800_odpowiedzi_na_opinie [c1]=1118_0700_rabat_czy_zadatek [c2]=1118_1200_polecenia [c3]=1118_1800_chatbot [d1]=1119_0700_zla_opinia [d2]=1119_1200_mailing_rabat [d3]=1119_1800_darmowa_dostawa [e1]=1120_0700_cena_z_dziewiatka [e2]=1120_1200_dopasowanie_i_format [e3]=1120_1800_algorytm_najtansze [f1]=1121_0700_czestotliwosc_reklamy [f2]=1121_1200_czas_odpowiedzi_lead [f3]=1121_1800_reklama_a_sklep [g1]=1122_0700_krotki_test_reklamy [g2]=1122_1200_lepsza_oferta [g3]=1122_1800_baner_w_telefonie [h1]=1123_0700_logo_w_reklamie [h2]=1123_1200_bf_koszt_reklamy)
for k in m2 m3 m4 z1 z2 z3 a1 a2 a3 b1 b2 b3 c1 c2 c3 d1 d2 d3 e1 e2 e3 f1 f2 f3 g1 g2 g3 h1 h2; do
  if [ $k != g1 ]; then ./zrob.sh $k > /tmp/zrob_$k.log 2>&1 || { echo "$k BLAD"; continue; }; fi
  cp /home/claude/hf/${k}e.mp4 $R/${M[$k]}_s6e.mp4
  echo "$k $(grep -E 'ruch|CIECIA|LUFS' /tmp/zrob_$k.log 2>/dev/null | tr '\n' ' ')"
done
echo KONIEC
# UWAGA (13.11 22:49): Metricool trzyma w pamieci podreczej stary plik spod tego samego adresu raw/main.
# Przy podmianie filmu podawaj adres z numerem commita: raw.githubusercontent.com/beetleads/beetleads-rolki/<sha>/plik.mp4
