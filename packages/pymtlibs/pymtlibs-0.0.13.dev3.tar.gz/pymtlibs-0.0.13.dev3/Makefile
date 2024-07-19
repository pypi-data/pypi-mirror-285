.PHONY: init
init:
	@bin/init_python.sh

.PHONY: docker_prune
docker_prune:
	@echo 清理 docker 无用镜像
	@sudo docker system prune -f



# make pip_publish
.PHONY: pip_publish
pip_publish:
	rm -rdf ./dist/* \
	&& . .venv/bin/activate \
	&& python -m build \
	&& python -m twine check dist/* \
	&& python -m twine upload --config-file .pypirc --repository pypi dist/*


# make docker_prune && make docker_build_mtmai
.PHONY: docker_build_mtmai
docker_build_mtmai:
	docker build --progress=plain -t gitgit188/mtmai:latest \
	--file Dockerfile \
	--target mtmai . \
	&& docker push gitgit188/mtmai:latest