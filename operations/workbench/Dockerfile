FROM oven/bun:1.3.9 AS build

WORKDIR /workbench
COPY package.json bun.lock ./
RUN bun install --frozen-lockfile
COPY src ./src
RUN bun build src/cli.ts --target=node --outfile /output/rossovia.mjs \
  && chmod 755 /output/rossovia.mjs

FROM scratch AS export
COPY --from=build /output/ /
