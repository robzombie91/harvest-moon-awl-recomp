cmake_minimum_required(VERSION 3.20)
project(hmawl C CXX)
set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 20)
add_subdirectory(gcn-recomp)
gcn_enable_languages()
gcn_add_game(
  NAME hmawl
  TITLE "Harvest Moon: A Wonderful Life"
  LABEL "Harvest Moon Recomp"
  DISC_ID GYWEE9
  DOL_SHA1 1ccfd9dfb5c250c2f45c70c74cc45e5d88d22374
  SYMBOLS ${CMAKE_SOURCE_DIR}/analysis/symbols.txt
  TABLES ${CMAKE_SOURCE_DIR}/recomp
  FPS 60
    RELS
        wlp0.rel
        wlp1.rel
        wlp2.rel
    REL_SYMBOLS ${CMAKE_SOURCE_DIR}/analysis/rel-symbols
)
