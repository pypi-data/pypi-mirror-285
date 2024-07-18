.PHONY: init
init:
	@bin/init_python.sh

.PHONY: docker_prune
docker_prune:
	@echo 清理 docker 无用镜像
	@sudo docker system prune -f



.PHONY: pip_publish
pip_publish:
	rm -rdf ./dist/* \
	&& python -m build \
	&& twine check dist/* \
	&& twine upload --config-file .pypirc --repository pypi dist/*


