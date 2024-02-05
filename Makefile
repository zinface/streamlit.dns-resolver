all:
	@echo "本次构建为说明: "
	@echo "  1. 进入 venv 模式"
	@echo "  2. 使用 pip 安装 streamlit"
	@echo "  3. 执行 streamlit run welcom.py，可使用 make run"



WHICH_STREAMLIT=$(shell which streamlit)
ifneq ($(WHICH_STREAMLIT),)
run:
	@streamlit run welcome.py
else 
run:
	@echo "NOTE: 当前环境中未发现 streamlit ，确保已执行 pip install streamlit"
endif
