# Slide bảo vệ cuối kỳ. Speaker notes lấy từ kich-ban-bao-ve.md (Lời nói + Chuyển ý của từng slide).
#   make        -> final-defense.pdf (XeLaTeX, như trước)
#   make notes  -> final-defense-notes.pdf: slide bên trái, lời nói bên phải. Dùng LuaLaTeX vì XeLaTeX làm mất
#                  màu chữ ở nửa slide khi có pgfpages.
TALK ?= kich-ban-bao-ve.md
XE  := xelatex -interaction=nonstopmode -halt-on-error
LUA := lualatex -interaction=nonstopmode -halt-on-error

all: final-defense.pdf
notes: final-defense-notes.pdf

notes.tex: $(TALK) make_notes.py
	python3 make_notes.py $(TALK)

DEPS := final-defense.tex beamerthemeHUST.sty notes.tex $(wildcard images/*)

final-defense.pdf: $(DEPS)
	$(XE) final-defense.tex >/dev/null && $(XE) final-defense.tex >/dev/null

final-defense-notes.pdf: $(DEPS)
	$(LUA) -jobname=final-defense-notes '\def\shownotes{1}\input{final-defense.tex}' >/dev/null && \
	$(LUA) -jobname=final-defense-notes '\def\shownotes{1}\input{final-defense.tex}' >/dev/null

clean:
	rm -f *.aux *.log *.nav *.out *.snm *.toc *.vrb *.xdv

.PHONY: all notes clean
